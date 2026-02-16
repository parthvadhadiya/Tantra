# Vendoring Tantra into Your Project

Tantra is designed to be **vendorable** - copy it into your project and make it yours. No pip install required (except for OpenAI SDK).

## Why Vendor?

Instead of installing Tantra as a dependency, you can copy the source code directly into your project:

✅ **Full Control** - Modify any behavior for your specific needs  
✅ **Zero Magic** - See and understand every line of code  
✅ **No Framework Lock-in** - It's your code now  
✅ **Learn by Reading** - Understand exactly how agent systems work  
✅ **Custom Optimizations** - Tune for your use case  

## Quick Start: Vendor the Core

### Step 1: Copy the Code

```bash
# Copy Tantra's core into your project
cp -r tantra/ myproject/agents/

# Or copy to a different location
cp -r tantra/ myproject/lib/ai/
```

### Step 2: Install Only OpenAI

```bash
pip install openai  # Only external dependency!
```

### Step 3: Use It

```python
# Import from your vendored copy
from myproject.agents import Agent

agent = Agent(
    name="MyAgent",
    system_message="You are helpful...",
    model="gpt-4o"
)

response = await agent.run("Hello!")
```

### Step 4: Make It Yours

Now you can modify anything:
- Change how tools are executed
- Add custom logging
- Modify provider behavior
- Optimize for your use case
- Add new features

**It's not "using Tantra" - it's YOUR agent code.**

## What to Vendor

### Minimal (300 lines)

Copy just the core - everything you need:

```bash
cp -r tantra/__init__.py myproject/agents/
cp -r tantra/agent.py myproject/agents/
cp -r tantra/providers.py myproject/agents/
cp -r tantra/types.py myproject/agents/
cp -r tantra/tools.py myproject/agents/
cp -r tantra/utils.py myproject/agents/
```

### With Examples

Copy examples as starting patterns:

```bash
cp -r tantra/ myproject/agents/
cp -r examples/ myproject/agents/examples/
```

## Staying Updated

Since you've vendored the code, YOU control updates.

### Check for Updates

Periodically check the [Tantra repo](https://github.com/axlnet/tantra) for:
- 🐛 Bug fixes you want to port
- ✨ New features you want to adopt
- 🚀 Performance improvements
- 📘 New patterns in examples/

### Port What You Want

```bash
# See what changed
git diff v0.1.0..main tantra/

# Port specific fixes you want
# (Just copy-paste or manually apply changes)
```

**You decide** what to adopt and when. No forced upgrades!

## Customization Ideas

Once vendored, common customizations:

### 1. Add Custom Logging

```python
# In agent.py
def _call_openai(self):
    logger.info(f"Calling LLM for user {self.user_id}")  # Your custom field
    # ... rest of method
```

### 2. Add Rate Limiting

```python
# In providers.py
class OpenAIProvider(LLMProvider):
    async def create_completion(self, ...):
        await self.rate_limiter.acquire()  # Your rate limiter
        # ... rest of method
```

### 3. Add Custom Tool Validation

```python
# In tools.py
def execute_tool(tool_name, tool_args, tool_map):
    if not validate_tool_args(tool_args):  # Your validation
        return {"success": False, "error": "Invalid args"}
    # ... rest of function
```

### 4. Add Metrics

```python
# In agent.py
async def run(self, task):
    start_time = time.time()
    result = await self._run_internal(task)
    self.metrics.record_duration(time.time() - start_time)  # Your metrics
    return result
```

### 5. Custom Provider

```python
# In your project
from myproject.agents.providers import LLMProvider

class MyCustomProvider(LLMProvider):
    # Your implementation for internal LLM, Ollama, etc.
    pass
```

## Hybrid Workflow

You can use both approaches:

```bash
# Quick prototyping - use pip install
pip install tantra

# Production - vendor and customize
cp -r $(python -c "import tantra; print(tantra.__path__[0])") myproject/agents/
```

## Vendoring Best Practices

### 1. Document Your Changes

```python
# agents/agent.py

# CUSTOMIZATION (2026-02-14): Added user_id tracking
# Original Tantra didn't track users, we need it for billing
self.user_id = user_id
```

### 2. Keep a CHANGELOG

```markdown
# myproject/agents/CHANGELOG.md

## Customizations from Tantra v0.1.0

- Added user_id tracking for billing
- Custom rate limiter for API costs
- Modified tool execution timeout to 60s
```

### 3. Commit Separately

```bash
# Initial vendor
git add myproject/agents/
git commit -m "Vendor Tantra v0.1.0"

# Your changes
git add myproject/agents/agent.py
git commit -m "Add user_id tracking to agents"
```

This makes it easier to update later.

## FAQ

**Q: Will I get security updates?**  
A: You need to check and manually apply them. Trade-off for full control.

**Q: Can I still contribute back?**  
A: Yes! If you make a general improvement, submit a PR to the main repo.

**Q: What if I want to switch back to pip install?**  
A: Remove your vendored copy, `pip install tantra`, update imports. Your custom changes will need to be re-applied.

**Q: How much code am I copying?**  
A: ~1200 lines total (including docstrings and comments). Small enough to read and understand completely.

**Q: Is this recommended?**  
A: If you need customization or hate "framework magic" - YES! Otherwise, `pip install` is fine.

## Support

Vendored code is YOUR code, but we're here to help:

- **Questions**: GitHub Discussions
- **Bug Reports**: Check if it's in upstream Tantra
- **Ideas**: Share your customizations in Discussions!

---

**Remember**: Once vendored, this is YOUR code. Modify it, optimize it, make it perfect for your use case. That's the whole point! 🚀
