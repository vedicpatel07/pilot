curl -X POST "http://localhost:8000/act" \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_encoded_image", "instruction": "pick up the cup"}'


to setup and run on tensorcore:
```bash
ssh -p 20097 user@193.200.65.142
git clone https://github.com/vedicpatel07/pilot.git
cd pilot/server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python deploy.py
```