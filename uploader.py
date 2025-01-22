import subprocess
import requests.auth
import click
import threading
import queue
import sys
import requests




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
@click.option('--passphrase', default="iSbyHu2SNRDV2GGTcHadcdscecg8nZR4S3Tsk", help='GPG symmetric passphrase')
@click.option('--name',default="file", help='Filename for pixeldrain')
@click.option('--apikey',default="5ecf0f8e-e7bb-4fba-ac3a-cdb9d0e661ae", help='API key for pixeldrain')

def upload(passphrase, name,apikey):
    """Wrapper for gpg and wget to upload files to pixeldrain encrypted, expects file on stdin."""
    # quesize can be limited in case producing is faster then streaming
    q = WriteableQueue(100)
    t=threading.Thread(target=post_request, args=(q,name,apikey))
    t.start()
    gpg=subprocess.Popen(["gpg","--passphrase",passphrase,'--compress-algo', 'none',"--batch","--with-colons","--symmetric"],
                         stdin=sys.stdin,
                         stdout=subprocess.PIPE)
    
    for chunk in iter(lambda:gpg.stdout.read(1000000),b""):
        q.write(chunk)
        
    q.close()
    t.join()
    
    
if __name__ == '__main__':
    upload()
    
