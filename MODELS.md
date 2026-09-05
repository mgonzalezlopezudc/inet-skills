# Specialist model classes

This is an overview of model bindings for the semantic specialist classes. Classes describe the
kind of work, so different classes may intentionally share a model binding. The platform runner
configuration is authoritative when a binding differs from this table.

| Class | Codex | Antigravity | Kimi |
| --- | --- | --- | --- |
| Reasoning | GPT-6 Astra, medium | Gemini 3.8 Flash, high | Kimi K3, max |
| Navigation | GPT-6 Astra, low | Gemini 3.8 Flash, medium | Kimi K3, high |
| Implementation | GPT-5.6 Luna, xhigh | Gemini 3.8 Flash, medium | Kimi K3, high |
| Extraction | GPT-5.6 Luna, xhigh | Gemini 3.8 Flash, low | Kimi K3, low |
