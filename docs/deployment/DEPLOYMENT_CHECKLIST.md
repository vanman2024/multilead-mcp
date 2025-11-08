# Deployment Checklist

Use this checklist to ensure successful deployment of the Multilead MCP Server.

## Pre-Deployment

### Code Quality

- [ ] All code changes committed to git
- [ ] No hardcoded API keys or secrets in code
- [ ] `.env.example` updated with new variables
- [ ] `.gitignore` includes `.env` and `logs/`
- [ ] Dependencies listed in `pyproject.toml`
- [ ] Version number updated in `server.py`

### Testing

- [ ] Server starts successfully in STDIO mode
- [ ] Server starts successfully in HTTP mode
- [ ] Health endpoint returns 200 OK
- [ ] All tools tested and working
- [ ] Error handling tested
- [ ] Rate limiting tested (if applicable)

### Configuration

- [ ] `.env` file created from `.env.example`
- [ ] Production API key configured
- [ ] Transport mode configured (stdio/http)
- [ ] Logging level appropriate for environment
- [ ] Rate limits configured
- [ ] Timeout values set

## STDIO Deployment (IDE Integration)

### Environment Setup

- [ ] Virtual environment created
- [ ] Dependencies installed: `pip install -e .`
- [ ] `.env` file configured
- [ ] MULTILEAD_API_KEY set
- [ ] TRANSPORT=stdio

### IDE Configuration

- [ ] IDE config file location confirmed
- [ ] Absolute path to server.py used
- [ ] Environment variables included in config
- [ ] Virtual environment path correct
- [ ] IDE/application restarted

### Verification

- [ ] Server appears in MCP servers list
- [ ] Connection successful
- [ ] Tools list populated
- [ ] Test tool execution successful
- [ ] No errors in IDE logs

## HTTP Deployment (Remote Access)

### Local Testing

- [ ] Server starts on configured port
- [ ] Health endpoint accessible
- [ ] MCP endpoint responding
- [ ] Rate limiting working
- [ ] Logging to file working
- [ ] Error handling working

### Production Server Setup

- [ ] Server/VPS provisioned
- [ ] Python 3.10+ installed
- [ ] Required system packages installed
- [ ] Firewall configured (allow port)
- [ ] User account created (non-root)
- [ ] Project directory created

### Application Deployment

- [ ] Code deployed to server
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file created (production values)
- [ ] Logs directory created
- [ ] File permissions set correctly

### Process Management

- [ ] Systemd service created (or supervisor/docker)
- [ ] Service enabled for auto-start
- [ ] Service started successfully
- [ ] Service status verified
- [ ] Service logs checked

### Reverse Proxy (nginx/caddy)

- [ ] Reverse proxy installed
- [ ] Server block configured
- [ ] Proxy headers set correctly
- [ ] Health check endpoint configured
- [ ] SSL certificate obtained (Let's Encrypt)
- [ ] HTTPS configured and tested
- [ ] HTTP to HTTPS redirect configured

### Security

- [ ] Production API keys used (not development)
- [ ] HTTPS/SSL enabled
- [ ] Firewall rules configured
- [ ] Rate limiting enabled
- [ ] Access logs enabled
- [ ] Error logs monitored
- [ ] Secrets not in version control

## Post-Deployment Verification

### Basic Functionality

- [ ] Server responding to requests
- [ ] Health check returns 200 OK
- [ ] MCP endpoint accepts requests
- [ ] All tools available
- [ ] Test tool execution successful

### Performance

- [ ] Response time acceptable (<2s)
- [ ] Memory usage reasonable
- [ ] CPU usage reasonable
- [ ] No memory leaks observed
- [ ] Rate limiting effective

### Monitoring

- [ ] Health check endpoint working
- [ ] Logs being written
- [ ] Log rotation configured
- [ ] Disk space sufficient
- [ ] Monitoring/alerting configured (if applicable)

### Error Handling

- [ ] Invalid requests handled gracefully
- [ ] API errors logged correctly
- [ ] Timeout errors handled
- [ ] Rate limit errors returned correctly
- [ ] 500 errors logged with stack traces

## Production Configuration

### Environment Variables

- [ ] MULTILEAD_API_KEY (production key)
- [ ] MULTILEAD_BASE_URL (correct API endpoint)
- [ ] TRANSPORT (http or stdio)
- [ ] HOST (0.0.0.0 or specific IP)
- [ ] PORT (8000 or custom)
- [ ] LOG_LEVEL (INFO for production)
- [ ] LOG_FORMAT (json for production)
- [ ] RATE_LIMIT_PER_MINUTE (configured)
- [ ] RATE_LIMIT_PER_HOUR (configured)
- [ ] MULTILEAD_TIMEOUT (configured)

### Security Hardening

- [ ] API keys rotated regularly
- [ ] Separate keys per environment
- [ ] HTTPS enforced
- [ ] CORS configured (if needed)
- [ ] Rate limiting active
- [ ] Access logs monitored
- [ ] Failed request alerts configured

## Documentation

- [ ] Deployment documented
- [ ] Environment variables documented
- [ ] API key rotation process documented
- [ ] Rollback procedure documented
- [ ] Monitoring procedures documented
- [ ] Troubleshooting guide updated
- [ ] Contact information current

## Client Configuration

- [ ] Client config files created
- [ ] Correct endpoint URL
- [ ] Authentication configured (if needed)
- [ ] Client tested successfully
- [ ] Multiple clients tested (if applicable)
- [ ] Documentation provided to users

## Rollback Plan

- [ ] Previous version tagged in git
- [ ] Rollback procedure documented
- [ ] Database backup taken (if applicable)
- [ ] Configuration backed up
- [ ] Rollback tested in staging

## Maintenance

- [ ] Backup strategy defined
- [ ] Update schedule defined
- [ ] Monitoring dashboard configured
- [ ] Alert recipients configured
- [ ] On-call rotation defined
- [ ] Incident response plan documented

## Sign-Off

- [ ] Technical lead approval
- [ ] Security review completed
- [ ] Load testing completed (if applicable)
- [ ] Documentation reviewed
- [ ] Users notified
- [ ] Support team briefed

---

**Deployment Date:** _________________

**Deployed By:** _________________

**Environment:** ☐ Development ☐ Staging ☐ Production

**Deployment Method:** ☐ STDIO ☐ HTTP ☐ Both

**Notes:**

_______________________________________________
_______________________________________________
_______________________________________________
