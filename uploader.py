import subprocess
import requests.auth
import click
import threading
import queue
import sys
import requests
import yaml


# from https://stackoverflow.com/questions/37310718/mutually-exclusive-option-groups-in-python-click
from click import Option, UsageError
class MutuallyExclusiveOption(Option):
    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
        help = kwargs.get('help', '')
        if self.mutually_exclusive:
            ex_str = ', '.join(self.mutually_exclusive)
            kwargs['help'] = help + (
                ' NOTE: This argument is mutually exclusive with '
                ' arguments: [' + ex_str + '].'
            )
        super(MutuallyExclusiveOption, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise UsageError(
                "Illegal usage: `{}` is mutually exclusive with "
                "arguments `{}`.".format(
                    self.name,
                    ', '.join(self.mutually_exclusive)
                )
            )

        return super(MutuallyExclusiveOption, self).handle_parse_result(
            ctx,
            opts,
            args
        )


class WriteableQueue(queue.Queue):

    def write(self, data):
        # An empty string would be interpreted as EOF by the receiving server
        #if data:
        self.put(data)

    def __iter__(self):
        return iter(self.get, None)

    def close(self):
        self.put(None)



def post_request(iterable,name,apikey):
    basic = requests.auth.HTTPBasicAuth('', apikey)
    response = requests.put(
        "https://pixeldrain.com/api/file/"+ name+".gpg" ,
        data=iterable,
        auth=basic
    )
    print(response.json()) 


@click.command()

@click.option('-n', '--name',default="file", help='Filename for pixeldrain')
@click.option('-k', '--apikey',cls=MutuallyExclusiveOption,mutually_exclusive=["secrets"], help='API key for pixeldrain')
@click.option('-p', '--passphrase',cls=MutuallyExclusiveOption,mutually_exclusive=["secrets"], help='GPG symmetric passphrase')
@click.option('-s', '--secrets',type=click.File(mode='r'),cls=MutuallyExclusiveOption, mutually_exclusive=["apikey","passphrase"],help="yaml file, can contain apikey and passphrase")
@click.argument('file', type=click.File(mode="rb"))

def upload(passphrase, name,apikey,file,secrets):
    """Wrapper for gpg and the pixeldrain API to upload files to pixeldrain encrypted, provide file to upload as argument, - to use stdin"""
    
    if(secrets):
        s=yaml.safe_load(secrets)
        if "apikey" in s.keys():
            apikey=s["apikey"]
        if "passphrase" in s.keys():
            passphrase=s["passphrase"]
    if not (apikey and passphrase):
        raise UsageError("Provide an API key and an encryption passphrase!")
    
    if(file):
        input_stream=file
        if name=="file" and file.name!="<stdin>":
            name=file.name
    else:
        input_stream=sys.stdin
    
    # quesize can be limited in case producing is faster then streaming
    q = WriteableQueue(100)
    t=threading.Thread(target=post_request, args=(q,name,apikey))
    t.start()
    gpg=subprocess.Popen(["gpg","--passphrase",passphrase,'--compress-algo', 'none',"--batch","--with-colons","--symmetric"],
                         stdin=input_stream,
                         stdout=subprocess.PIPE)
    
    for chunk in iter(lambda:gpg.stdout.read(1000000),b""):
        q.write(chunk)
        
    q.close()
    t.join()
    
    
if __name__ == '__main__':
    upload()
    
