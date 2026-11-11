# Chaibao_DigitaldeskPet

柴宝是按照片制作的 ChatGPT 桌宠，保留了黑色短毛、金色眼睛和略圆的脸颊。Windows 桌面端已安装并确认显示。

[安装与显示](docs/INSTALL.md) · [动画预览](docs/preview/chaibao.gif) · [制作记录](docs/WORKFLOW.md)

## 项目结构

- `assets/source/` 保存定稿形象和各动作的源图。
- `assets/pet/spritesheet.png` 是通过 Pets 校验的透明图集。
- `tools/render_previews.py` 生成预览，`tools/vendor/` 保存 Pets 插件的原版制作和校验工具。

## 生成预览

在项目根目录运行以下命令。输出位于 `build/previews/`。

```powershell
python -m pip install -r requirements.txt
python tools/render_previews.py
```

## 同步到 GitHub

此工作副本已启用提交后推送。新克隆的副本可运行 `git config core.hooksPath .githooks` 启用同一行为。推送失败时，提交保留在本地，可运行 `git push` 重试。
