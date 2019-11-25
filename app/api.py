from flask import Flask,redirect,render_template
import requests
app = Flask(__name__)


@app.route('/')
def hello():
    url='https://account-d.docusign.com/oauth/auth'
    response_type="code"
    scope="signature"
    client_id="3d6303f3-6792-4a6a-86bf-df56834e740d"
    state="a39fh23hnf23"
    redirect_uri="http://localhost:5000/ds/callback"
    params={'response_type':'code','scope':"signature",'client_id':"3d6303f3-6792-4a6a-86bf-df56834e740d",'state':"a39fh23hnf23",'redirect_uri':"http://localhost:5000/ds/callback"}
    res=requests.get(url=url , params=params)
    print(res.text)
    return render_template(res.text)
    #return redirect(res.text)
    #return "Hello World!"

if __name__ == '__main__':
    app.run()