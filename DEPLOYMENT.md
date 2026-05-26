# Deployment & Production Guide
## English-Luganda Translator

---

## Quick Start (Development)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Flask Server
```bash
python web_server_flask.py
```

### 3. Access Application
- Web Interface: http://localhost:5000
- API Docs: http://localhost:5000/api/docs
- Health Check: http://localhost:5000/api/health

---

## API Endpoints

### Health & Status

**GET /api/health**
- Monitor server health
- Response: `{status, model_loaded, device, timestamp}`

**GET /api/status**
- Detailed status information
- Response: `{model_loaded, device, gpu_available, torch_version}`

**GET /api/docs**
- API documentation
- Returns all available endpoints

### Translation

**POST /api/translate** (Single)
- Request: `{text: "Hello"}`
- Response: `{english, luganda, success, timestamp}`
- Rate limit: 100 requests/hour

**POST /api/translate-batch** (Multiple)
- Request: `{texts: ["Hello", "Good morning"]}`
- Response: `{results: [...], errors: [...], summary: {}}`
- Max batch size: 50 texts
- Rate limit: 50 requests/hour

---

## Logging

Logs are automatically saved to `logs/` directory with timestamps.

### Log Levels
- INFO: Normal operations
- WARNING: Validation errors, rate limits
- ERROR: Model errors, server errors

### Access Logs
```bash
tail -f logs/translator_*.log
```

---

## Docker Deployment

### Build Image
```bash
docker build -t english-luganda-translator .
```

### Run Container
```bash
docker run -p 5000:5000 english-luganda-translator
```

### Using Docker Compose
```bash
docker-compose up -d
```

### Check Container Health
```bash
docker ps
docker logs -f english-luganda-translator
```

---

## Production Configuration

### 1. Create .env file (from .env.example)
```bash
cp .env.example .env
```

### 2. Configure Settings
Edit `.env` for production:
```
FLASK_ENV=production
FLASK_DEBUG=False
DEVICE=cuda  # Use GPU if available
MAX_BATCH_SIZE=50
RATE_LIMIT_REQUESTS=100
WORKERS=4
```

### 3. Use Production Server

**With Gunicorn** (recommended)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_server_flask:app
```

**With Waitress**
```bash
pip install waitress
waitress-serve --port=5000 web_server_flask:app
```

---

## Performance Optimization

### 1. GPU Usage
- Ensure CUDA is installed
- Check: `nvidia-smi`
- Set `DEVICE=cuda` in config

### 2. Batch Processing
- Use `/api/translate-batch` for multiple texts
- More efficient than single requests
- Max 50 texts per request

### 3. Caching
- Consider implementing Redis for translation cache
- Cache common phrases for faster response

### 4. Model Optimization
- Consider quantization for smaller model size
- Use smaller beam size (2-4) for faster inference

---

## Monitoring

### Health Check Command
```bash
curl http://localhost:5000/api/health
```

### Request Count
- Check logs for request frequency
- Monitor rate limit violations

### Performance Metrics
- Check inference time in logs
- Monitor GPU memory usage: `nvidia-smi`

---

## Testing

### Run API Tests
```bash
python test_api.py
```

### Manual Testing
```bash
# Single translation
curl -X POST http://localhost:5000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}'

# Batch translation
curl -X POST http://localhost:5000/api/translate-batch \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Hello", "Good morning"]}'
```

---

## Troubleshooting

### Model Not Found
- Ensure model is trained first
- Check path: `models/trained_model/`

### GPU Not Available
- Server defaults to CPU automatically
- Check CUDA installation: `nvidia-smi`

### Rate Limit Exceeded
- Default: 100 requests/hour per IP
- Adjust in `.env` or code

### Memory Issues
- Reduce batch size
- Use CPU instead of GPU
- Implement model quantization

### Connection Issues
- Check port 5000 is available
- Firewall configuration
- Try different host: `0.0.0.0` for all interfaces

---

## Production Checklist

- [ ] Model trained and saved
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] Logs directory created
- [ ] Health check passing
- [ ] API test script successful
- [ ] Rate limiting configured
- [ ] CORS enabled for needed domains
- [ ] SSL/TLS certificate (for HTTPS)
- [ ] Database backup strategy
- [ ] Monitoring setup
- [ ] Error alerts configured

---

## Security Considerations

1. Input Validation: All inputs sanitized
2. Rate Limiting: Prevent abuse (100 requests/hour)
3. CORS: Restrict to trusted domains
4. Logging: Track all requests and errors
5. Error Messages: Don't expose internal details
6. Dependencies: Regularly update packages

---

## Scaling

### Horizontal Scaling
- Deploy multiple instances
- Use load balancer (nginx, HAProxy)
- Share model across instances

### Vertical Scaling
- Use GPU for acceleration
- Increase batch size
- Optimize model (quantization, distillation)

---

## Support & Issues

- Check logs: `logs/translator_*.log`
- API docs: `/api/docs`
- Health check: `/api/health`
- Contact project maintainer for issues
