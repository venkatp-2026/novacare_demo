FROM python:3.10-slim

# Create a non-root user for security compliance
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:${PATH}"

WORKDIR /app

# Copy and install requirements
COPY --chown=user:user requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy application files
COPY --chown=user:user . /app

# Expose the mandatory Hugging Face port
EXPOSE 7860

# Bind to 0.0.0.0 and listen on 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
