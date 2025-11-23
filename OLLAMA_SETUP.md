# Ollama Setup Guide for Dev-Standup

Complete guide to installing and configuring Ollama for Dev-Standup Automator.

## Windows Installation

### Step 1: Download Ollama

**Option A - Direct Download:**
Visit: [ollama.com/download/windows](https://ollama.com/download/windows)

**Option B - PowerShell:**
```powershell
Invoke-WebRequest -Uri "https://ollama.com/download/OllamaSetup.exe" -OutFile "$env:TEMP\OllamaSetup.exe"
Start-Process "$env:TEMP\OllamaSetup.exe"
```

### Step 2: Install

1. Run `OllamaSetup.exe`
2. Follow the installation wizard
3. **Important:** Restart your terminal after installation

### Step 3: Verify Installation

```bash
ollama --version
```

You should see: `ollama version is 0.x.x`

### Step 4: Pull AI Model

```bash
# Download llama2 model (~4GB, takes a few minutes)
ollama pull llama2
```

**Alternative Models:**
```bash
ollama pull phi        # ~1.6GB - faster, smaller
ollama pull mistral    # ~4GB - higher quality
ollama pull codellama  # ~4GB - optimized for code
```

### Step 5: Start Ollama Server

```bash
# Start Ollama server (runs in background)
ollama serve
```

**Keep this terminal open** while using dev-standup.

**Note:** After installation, Ollama usually auto-starts on system boot. You may not need to run `ollama serve` manually after a restart.

## Test Ollama

Verify everything works:

```bash
# Test with a simple prompt
ollama run llama2 "Hello, what is your name?"
```

If you get a response, Ollama is working correctly!

## Troubleshooting

### "ollama: The term 'ollama' is not recognized"

**Cause:** Terminal hasn't picked up PATH changes.

**Solution 1 (Best):** Restart terminal completely
- Close PowerShell/Terminal window
- Open a new one
- Run `ollama --version`

**Solution 2:** Use full path immediately
```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" --version
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" pull llama2
```

**Solution 3:** Refresh environment variables
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
ollama --version
```

---

### "Cannot connect to Ollama" / "Read timed out"

**Cause:** Ollama server is not running.

**Solution:** Start Ollama in a separate terminal
```bash
ollama serve
```

Leave this terminal open while using dev-standup.

**Check if Ollama is running:**
```powershell
Get-Process ollama -ErrorAction SilentlyContinue
```

If you see processes listed, Ollama is running.

**Auto-start:** After installation and system restart, Ollama should start automatically. You won't need to run `ollama serve` manually.

---

### Model Download is Slow

**Cause:** Large model size (~4GB for llama2).

**Solutions:**
- Be patient - downloads can take 5-15 minutes depending on connection
- Use a smaller model: `ollama pull phi` (~1.6GB)
- Check download progress - Ollama shows progress bar
- Ensure stable internet connection

---

### "Model not found"

**Cause:** Haven't pulled the model yet.

**Solution:**
```bash
ollama pull llama2
```

**Available models:**
- `llama2` - General purpose, good quality
- `phi` - Small, fast
- `mistral` - High quality
- `codellama` - Code-specific

---

### High Memory Usage

**Cause:** LLM models use GPU/RAM.

**Expected:** llama2 uses ~4-8GB RAM when running.

**Solutions:**
- Use smaller model: `phi` uses ~2-3GB
- Close Ollama when not in use
- Upgrade RAM if running many applications

---

### Permission Errors

**Cause:** Installation requires admin rights.

**Solution:**
- Right-click installer → "Run as administrator"
- Or run PowerShell as administrator

## Configure Dev-Standup

After Ollama is installed, configure Dev-Standup:

### 1. Copy Environment File

```bash
cp .env.example .env
```

### 2. Edit `.env` (Optional)

Default settings work out of the box:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
DEFAULT_MOOD=neutral
```

**To use a different model:**
```env
OLLAMA_MODEL=mistral  # or phi, codellama, etc.
```

### 3. Test Dev-Standup

```bash
python run.py --repo voice_bot --all-authors
```

If you see an AI-generated summary, everything is working! 🎉

## Advanced Configuration

### Change Ollama Port

If port 11434 is in use:

1. Start Ollama on different port:
```bash
OLLAMA_HOST=127.0.0.1:11435 ollama serve
```

2. Update `.env`:
```env
OLLAMA_BASE_URL=http://localhost:11435
```

### Use Different Model

Edit `.env`:
```env
OLLAMA_MODEL=mistral  # Better quality
# or
OLLAMA_MODEL=phi      # Faster, smaller
```

### GPU Acceleration

Ollama automatically uses GPU if available (NVIDIA/AMD).

Check GPU usage:
```bash
# Windows Task Manager → Performance → GPU
```

## Uninstall Ollama

If needed:

1. Windows Settings → Apps → Ollama → Uninstall
2. Remove models:
```powershell
Remove-Item "$env:USERPROFILE\.ollama" -Recurse -Force
```

## FAQ

**Q: Do I need internet after installation?**
A: No, once models are downloaded, Ollama runs 100% offline.

**Q: How much disk space do models use?**
A: llama2: ~4GB, phi: ~1.6GB, mistral: ~4GB

**Q: Can I use multiple models?**
A: Yes! Pull multiple models and switch in `.env`

**Q: Is my code sent to the cloud?**
A: No! Everything runs locally, your code never leaves your machine.

**Q: Can I use this on Mac/Linux?**
A: Yes! Ollama supports all platforms. Download from ollama.com

## Need Help?

- Ollama Documentation: [github.com/ollama/ollama](https://github.com/ollama/ollama)
- Dev-Standup Issues: Check the project GitHub
- Ollama Discord: [discord.gg/ollama](https://discord.gg/ollama)

---

Back to [README](README.md) | [Quick Start](QUICKSTART.md)
