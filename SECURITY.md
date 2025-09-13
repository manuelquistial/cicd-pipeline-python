# Security Configuration

## Secret Key Management

This application requires a secure SECRET_KEY for CSRF protection and session management.

### Development Setup

1. Copy the example environment file:
   ```bash
   cp env.example .env
   ```

2. Generate a secure secret key:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. Set the SECRET_KEY in your `.env` file:
   ```
   SECRET_KEY=your-generated-secret-key-here
   ```

### Production Setup

**IMPORTANT**: Never use the default secret key in production!

1. Set the SECRET_KEY environment variable:
   ```bash
   export SECRET_KEY="your-secure-production-secret-key"
   ```

2. Or use a secure key management system (AWS Secrets Manager, HashiCorp Vault, etc.)

### Security Features

- **CSRF Protection**: Enabled by default
- **Rate Limiting**: 200 requests per day, 50 per hour
- **Security Headers**: X-Frame-Options, X-XSS-Protection, etc.
- **Input Validation**: WTForms validation for all inputs
- **Error Handling**: Secure error messages without sensitive information

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Flask secret key | Generated for dev | Yes (production) |
| `FLASK_ENV` | Environment mode | development | No |
| `FLASK_DEBUG` | Debug mode | true | No |
| `CSRF_PROTECTION` | Enable CSRF | true | No |

### Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use strong, unique secret keys** for each environment
3. **Rotate secret keys** regularly in production
4. **Use HTTPS** in production
5. **Monitor for security vulnerabilities** regularly
