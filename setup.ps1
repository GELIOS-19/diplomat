if (-not(Test-Path backend\venv)) { 
    cd backend
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    echo "venv created"
    cd ..
}

if (-not(Test-Path frontend\node_modules)) {
    cd frontend
    npm install
    echo "node_modules created"
    cd ..
}
