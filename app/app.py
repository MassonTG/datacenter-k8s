from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    # Read secrets from Vault sidecar
    secrets = {}
    try:
        with open('/vault/secrets/config', 'r') as f:
            content = f.read()
            secrets['status'] = 'Vault connected!'
            secrets['content'] = content
    except:
        secrets['status'] = 'No Vault secrets found'

    return f'''
    <h1>Hello from GitLab CI/CD!</h1>
    <h2>Vault: {secrets["status"]}</h2>
    <pre>{secrets.get("content", "N/A")}</pre>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
