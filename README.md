# Chaibao_DigitaldeskPet

柴宝的数字桌面宠物：根据真实照片制作的黑色短毛、金色眼睛小猫。

这是 ChatGPT Pets 的动画素材与制作工具项目。桌面悬浮、交互和状态切换由宿主应用提供，本项目不包含独立 Windows 桌宠程序。

## 目录

- `assets/source/`：确认过的主形象与生成的动作素材；不包含原始生活照片。
- `assets/pet/`：通过验证后用于安装的透明精灵图。
- `tools/`：预览入口及原版制作、验证工具。
- `docs/`：安装说明、制作过程和验证记录。

## 本地预览

```powershell
python -m pip install -r requirements.txt
python tools/render_previews.py
```

最终素材就绪后，命令从 `assets/pet/spritesheet.png` 生成 `build/previews/` 下的 GIF、MP4 与逐帧预览。当前进度见 [制作记录](docs/WORKFLOW.md)。

## 更新方式

每完成一个可检查的阶段提交一次 Git 更新；最终动画验证通过后再更新安装素材。未完成或验证失败的图集不会作为成品发布。聊天结束后没有常驻自动上传服务。

## 工具来源

`tools/vendor/` 保留 Pets 插件 create-pet 0.1.6 的原版脚本，作为几何与质量验证依据；不以自写简单验证替代它们。`tools/render_previews.py` 是本项目的预览包装脚本。生成图像由 OpenAI 内置 imagegen 完成。

