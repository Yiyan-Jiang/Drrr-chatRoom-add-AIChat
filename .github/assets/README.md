# README 素材来源

本目录保存项目 README 使用的图片。Logo 与技术栈徽章使用现成素材并原样保存；平面构成海报按本次要求生成。

## DOLLARS Logo

`dollars-logo.png` 来自[本项目 GitHub 仓库已有的 Logo](https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat/blob/main/frontend/src/assets/icon/Logo/logo.png)，与前端使用的图片一致。

## 技术栈徽章

使用 [Shields.io](https://github.com/badges/shields) 提供的标准 `flat-square` 徽章，附带对应技术图标。徽章下载到本目录，README 不依赖远程图片请求。

| 本地文件         | 原始资源                                                                                                           |
| ---------------- | ------------------------------------------------------------------------------------------------------------------ |
| `python.svg`     | [Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)       |
| `react.svg`      | [React 19](https://img.shields.io/badge/React-19-20232A?style=flat-square&logo=react&logoColor=61DAFB)             |
| `typescript.svg` | [TypeScript 6](https://img.shields.io/badge/TypeScript-6-3178C6?style=flat-square&logo=typescript&logoColor=white) |
| `fastapi.svg`    | [FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)              |
| `socketio.svg`   | [Socket.IO](https://img.shields.io/badge/Socket.IO-010101?style=flat-square&logo=socketdotio&logoColor=white)      |
| `mysql.svg`      | [MySQL 8.4](https://img.shields.io/badge/MySQL-8.4-4479A1?style=flat-square&logo=mysql&logoColor=white)            |

徽章仅展示当前技术栈与文档建议的运行版本，不表示构建或业务测试已通过。依赖升级后需同步更新对应图片。

## DOLLARS 平面构成海报

`dollars-poster.png` 使用内置 `image_gen` 工具生成，主题延续《无头骑士异闻录》中的 DOLLARS 聊天室。海报采用镂空文字、局部反色人物蒙版、几何构图与英文、日文点缀，用于 README 简介和功能亮点之间。

<details>
<summary>完整生成提示词</summary>

```text
Use case: stylized-concept
Asset type: one finished flat graphic-design editorial poster to be placed in a GitHub README after the introduction, before feature highlights. Landscape composition, approximately 3:2 aspect ratio, high-resolution raster.
Primary request: Create a sophisticated flat-composition poster inspired by Durarara!! (無頭騎士異聞録), the DOLLARS anonymous chatroom, and Ikebukuro urban connections. This must look like an art-directed Japanese exhibition poster, with strong geometric composition, knockout typography and an inverted-color mask that occludes part of the character.
Subject: a single stylized Celty Sturluson figure wearing her iconic bright yellow cat-ear motorcycle helmet with dark visor and fitted black riding jacket, shown waist-up as a dramatic cropped illustration. Flat hard-edged graphic artwork, not a photograph, not a 3D render. The helmet and black rider silhouette should remain recognizable.
Composition: asymmetric rigorous typographic grid with large negative spaces, a large bold condensed DOLLARS wordmark and graphic character intersecting with circles, rectangles, diagonal bands and fine grid lines. Make several large letterforms genuinely cut-out / knockout, revealing the figure or underlying background through the letters. Place a sharply bounded rectangular difference / inverted-color mask across part of the helmet and torso, so the silhouette, underlying geometry and typography visibly reverse black and ivory inside the mask, with yellow shifted to a contrasting dark tone. Keep the graphic legible and intentional rather than random glitching. Crisp modular geometry and tightly controlled alignment. A few thin network paths subtly suggest anonymous chat connections.
Palette: high-contrast ink black, warm ivory, and saturated signal yellow, with subtle printed paper grain. Mostly flat screenprinted fields, no gradients, no glossy effects.
Typography: confident oversized cropped sans-serif typography, smaller precise English and Japanese editorial accents. Render these texts accurately: "DOLLARS" as the main headline; "IKEBUKURO" and "ANONYMOUS CONNECTION" as small English accents; "池袋" and "誰かと、つながる。" as Japanese accents. Use a short Japanese vertical text treatment as a compositional counterpoint. Do not add paragraphs or interface widgets.
Constraints: full-bleed flat 2D artwork, not a poster photographed in a room or on a wall. Keep important subject and lettering inside a sensible safe margin. Refined professional design, purposeful typographic hierarchy, expressive negative space. No fake app screenshot, no UI mockup, no chat-bubble clip art, no gradient tech banner, no extra people, no watermark.
```

</details>
