<div align="center">

### vivibibi

Android 逆向 · HyperOS 预装组件分析 · LSPosed 模块

[![followers](https://img.shields.io/github/followers/vivibibi30?style=flat-square&label=followers&color=0969da)](https://github.com/vivibibi30)
[![hyperpguard stars](https://img.shields.io/github/stars/vivibibi30/hyperpguard?style=flat-square&label=hyperpguard%20stars&color=0969da)](https://github.com/vivibibi30/hyperpguard/stargazers)
[![release](https://img.shields.io/github/v/release/vivibibi30/hyperpguard?style=flat-square&label=release&color=2da44e)](https://github.com/vivibibi30/hyperpguard/releases)
[![license](https://img.shields.io/github/license/vivibibi30/hyperpguard?style=flat-square&label=license&color=2da44e)](https://github.com/vivibibi30/hyperpguard/blob/main/LICENSE)

</div>

## 在做的事

**[HyperPGuard](https://github.com/vivibibi30/hyperpguard)** — 给小米 / 红米 HyperOS 的预装组件加一层可控的开关，在采集入口、本地存储、对外接口、网络出口四个环节拦掉隐私上报。按应用分组，开关与作用域实时联动；覆盖 12 个预装组件（含移动 DM `com.miui.dmregservice`、系统诊断 `com.miui.misightservice`），设备标识与敏感数据按应用单独开关，支持自定义域名 / 路径规则，libxposed API 102（`staticScope`），GPL-3.0。

| 环节 | 拦截对象 |
|---|---|
| 网络出口 | 目标进程内的 `URL` / `InetAddress` / `Socket`，规则为「域名后缀 + 路径」 |
| 本地存储 | 行为库 `SQLiteDatabase` 的 insert / update / delete / execSQL，按表名过滤 |
| 对外接口 | `XSOFProvider` 三入口、`MiSafetyDetectService` 的回调型方法（按末参 `IMiSafetyDetectCallback` 匹配）、评分与鉴权 |
| 采集入口 | 应用列表 / 使用记录 / 短信、静默录屏 `createVirtualDisplay`；设备标识与敏感数据按应用分项开关 |

识别目标靠静态逆向加真机验证：`jadx` / `apktool` 拆组件、`d8` 重打包试钩、`logcat` 看命中与 miss。组件混淆名逐版本变化，所以方法层只做签名扫描，能兜住的部分交给框架 API。

模块内带诊断面板：各应用注入状态、行为库写入计数、按未拦截 / 已拦截分段的日志。维护按需进行，只在出现影响使用的缺陷或发现新的上报通道时发版。

## 项目

| 仓库 | 说明 | 状态 |
|---|---|---|
| [hyperpguard](https://github.com/vivibibi30/hyperpguard) | HyperOS 隐私上报拦截模块（LSPosed） | Java · GPL-3.0 |
| [ghostlock-app](https://github.com/vivibibi30/ghostlock-app) | GhostLock 一键利用（CVE-2026-43499），fork 自 [YukongA/ghostlock-app](https://github.com/YukongA/ghostlock-app) | Kotlin · fork |

## 工具箱

![Android](https://img.shields.io/badge/Android-3DDC84?style=flat-square&logo=android&logoColor=white)
![Java](https://img.shields.io/badge/Java-21-ED8B00?style=flat-square&logo=openjdk&logoColor=white)
![Kotlin](https://img.shields.io/badge/Kotlin-2.x-7F52FF?style=flat-square&logo=kotlin&logoColor=white)
![Smali](https://img.shields.io/badge/Smali-反编译-6E4C13?style=flat-square)
![libxposed](https://img.shields.io/badge/libxposed-API%20102-0969da?style=flat-square)
![LSPosed](https://img.shields.io/badge/LSPosed-2.2.1-0969da?style=flat-square)
![KernelSU](https://img.shields.io/badge/KernelSU-root-2da44e?style=flat-square)
![Debian](https://img.shields.io/badge/Debian-chroot-A81D33?style=flat-square&logo=debian&logoColor=white)

日常用的：`jadx` · `apktool` · `aapt2` · `d8` · `apksigner` · `frida` · `logcat` · `git`

环境：HyperOS + KernelSU + LSPosed。

## 概览

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/stats-dark.svg">
  <img alt="GitHub 概览" src="assets/stats-light.svg" width="740">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/contrib-dark.svg">
  <img alt="近一年贡献" src="assets/contrib-light.svg" width="740">
</picture>

卡片由 [`scripts/gen_cards.py`](scripts/gen_cards.py) 通过 GitHub API 生成，每天自动更新。

## 说明

- 仓库内容用于在**本人拥有完全控制权**的设备上做系统行为分析与限制，不含针对他人的攻击能力
- 模块本体不联网、不收集、不上传任何信息，配置只存在本地
- 引用他人的识别结论时会在 README 里注明来源与作者，转载或二次分发请保留来源与许可证

问题、建议或复现信息，直接开 [Issue](https://github.com/vivibibi30/hyperpguard/issues)。
