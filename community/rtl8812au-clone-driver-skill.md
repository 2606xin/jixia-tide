---
title: RTL8812AU 克隆网卡驱动驯服术
author: 2606xin
tags:
  - windows
  - driver
  - hardware
  - network
  - troubleshooting
created_at: 2026-09-30
---

# RTL8812AU 克隆网卡驱动驯服术

淘宝/DIY 的 RTL8812AU 克隆芯片 USB WiFi 网卡（`USB\VID_0BDA&PID_881A`，设备名 `RTL8812AU-VS(802.11ac 2x2 USB2.0)`，序列号常为 "123456"）在 Windows 10/11 上的驱动安装与修复完整打法。实战验证于 Win11 26200（2026-09），从"插上就废"一路打到稳定运行。

## 背景真相（30 秒）

克隆芯片固件是非标准魔改版，Realtek 2016 年后的驱动带芯片固件版本校验，克隆货过不了检：

| 驱动版本 | 表现 | 结论 |
|---|---|---|
| 2019 / Win11 内置 (1030.38.x) | 绑得上、状态 OK，但**永远不出 MAC** | 静默失败，最骗人 |
| 2017 通用版 NW392 (1030.25.0701.2017) | 能出 MAC、能扫描，但每 ~2 秒报事件 5006"对本驱动程序而言，版本号错误"→复位芯片→USB 重枚举→"设备重新连接"弹窗风暴 | 不可用 |
| **2015 WHQL (1030.1.715.2015)** | 稳定 | **唯一正确答案** |

Win10 驱动装 Win11 完全没问题——系统兼容性从来不是障碍，芯片校验才是。

## 诊断（无需管理员）

```powershell
Get-PnpDevice -PresentOnly | ? {$_.InstanceId -match 'VID_0BDA'}
Get-NetAdapter | ? {$_.InterfaceDescription -like '*8812*'} | fl Name,Status,MacAddress
(Get-WinEvent -FilterHashtable @{LogName='System';Id=5006;StartTime=(Get-Date).AddMinutes(-5)} -ErrorAction SilentlyContinue | ? {$_.Message -match '8812'} | Measure-Object).Count
```

判读：MAC 空 + 状态 OK = 新驱动静默失败；5006 每几秒一条 = 版本校验复位循环；设备整个不在总线 = 没插好。

## 2015 驱动包验真（grep INF 三要素）

1. `DriverVer = 07/28/2015,1030.1.715.2015`
2. 含 `RTL8812au_Vx`（**后缀**形式 Vx 段）
3. 含 `USB\VID_0BDA&PID_881A`

注意：2017 NW392 通用版的 Vx 段是**前缀**形式 `Vx_RTL8812au.ndi`，形态相似——认准版本号。正版包文件夹名形如 `8812_wlan_1030_1_0715_2015_whql` / `realtek_rtl8812_1030.1.0715.2015\Win10\`。Microsoft Update Catalog 只有 2024+ 新版，找不到 2015 老包。

## 修复阶梯（顺序即胜率，全部实战验证）

1. `pnputil /add-driver <2015.inf> /install` 入库
2. `UpdateDriverForPlugAndPlayDevices`（INSTALLFLAG_FORCE=1，即图形界面"从磁盘安装→是"的等价物）强装——本文底部脚本已内置
3. 报 win32error 0xE000024B → **驱动库里存在更新版本的第三方 oem 包占位，Windows 拒绝降级替换**。读取当前绑定的 oemNN.inf，`pnputil /delete-driver <oemNN> /uninstall` 删掉后再强装。关键洞察：内置 inbox 包不挡路也删不掉，只有第三方 oem 包挡路
4. 删除/安装全被静默忽略（删驱动无输出、强装报错）= 驱动服务僵死态 → **重启是唯一解锁**，重启后重跑脚本
5. 装上后必须有一次**成功的**设备重启（`pnputil /restart-device` 输出"已成功重启设备"或物理拔插）才触发固件加载出 MAC——绑定成功 ≠ 芯片启动

## 验收（4 条全过）

1. `DEVPKEY_Device_DriverVersion` = 1030.1.715.2015
2. 接口 MAC 非空
3. `netsh wlan show networks interface="<8812的接口名>"` 能扫到网——**必须指定 interface**，默认输出显示的是机器内置 WiFi 卡的成绩
4. 观察窗内 5006 事件 = 0

## 善后

- Windows Update 以后可能推新驱动 → 症状复发（MAC 消失或 5006 风暴）→ 重跑脚本两分钟恢复；彻底封锁用微软 wushowhide 隐藏那条 Realtek 更新（只影响这一条；全局组策略会禁掉所有设备驱动更新，不推荐）
- 双网卡并存正常：内置卡 + 8812 可同时连不同 SSID；系统快速设置 WiFi 开关是全局的（一关全关）
- 8812 空闲时 Status 空/Disconnected、速率 0 bps 属正常，别误判成坏了

## 症状 → 根因速查

| 症状 | 根因 |
|---|---|
| 状态 OK 但接口无 MAC | 2019+/内置驱动静默失败 |
| 5006 每 ~2 秒一条 + "设备重新连接"弹窗风暴 | 2017 类驱动版本校验复位循环 |
| 强装始终 0xE000024B | 更新版第三方 oem 包占位挡降级 |
| 删驱动无输出、安装被静默忽略 | 僵死态，重启唯一解锁 |
| Disable 成功后 Enable 报"常规故障" | 卡在问题码 22（CM_PROB_DISABLED），先救回启用态 |
| restart-device 报"设备没有连接"但设备在 | 幽灵态，物理拔插一次可清 |

## 一键修复脚本（管理员 PowerShell 运行）

用法：把 2015 驱动包放纯 ASCII 路径（PS5.1 中文编码坑），管理员终端执行
`powershell -NoProfile -ExecutionPolicy Bypass -File fix-rtl8812au-2015.ps1 [-InfPath <2015目录>\netrtwlanu.inf]`
（默认 InfPath 为 `E:\rtl8812drv\Win10_2015\netrtwlanu.inf`）。退出码：0 成功 / 1 无设备 / 2 需重启后重跑 / 3 装上但不稳。

```powershell
param([string]$InfPath = 'E:\rtl8812drv\Win10_2015\netrtwlanu.inf')

# RTL8812AU clone-chip repair: force the 2015 WHQL driver (1030.1.715.2015) onto
# USB\VID_0BDA&PID_881A. Ladder proven on Win11 26200, 2026-09-29. Run elevated.

$ErrorActionPreference = 'Continue'
$logDir = Split-Path $InfPath -Parent
$log = Join-Path $logDir ('fix-rtl8812au_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.log')
Start-Transcript -Path $log -Force

$hwid = 'USB\VID_0BDA&PID_881A'

if (-not (Test-Path $InfPath)) {
  Write-Host "[!] INF not found: $InfPath - pass -InfPath or copy the 2015 driver to an ASCII path."
  Stop-Transcript; exit 1
}

$dev = Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -like ($hwid + '*') }
if (-not $dev) {
  Write-Host '[!] No VID_0BDA&PID_881A device on the USB bus. Plug the adapter in and re-run.'
  Stop-Transcript; exit 1
}
$id = $dev[0].InstanceId
Write-Host "device: $id"

function Get-Prop($key) { (Get-PnpDeviceProperty -InstanceId $id -KeyName $key -ErrorAction SilentlyContinue).Data }
function Get-Drv { Get-Prop 'DEVPKEY_Device_DriverVersion' }
function Get-InfPath { Get-Prop 'DEVPKEY_Device_DriverInfPath' }

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class NewDev {
  [DllImport("newdev.dll", CharSet=CharSet.Unicode, SetLastError=true)]
  public static extern bool UpdateDriverForPlugAndPlayDevices(IntPtr hwndParent, string HardwareId, string FullInfPath, uint InstallFlags, ref bool bRebootRequired);
}
'@

function Force2015 {
  $reboot = $false
  $ok = [NewDev]::UpdateDriverForPlugAndPlayDevices([IntPtr]::Zero, $hwid, $InfPath, 1, [ref]$reboot)
  $err = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
  Write-Host ("ForceInstall ok=$ok win32err=$err -> driver now: " + (Get-Drv))
}

Write-Host ("current: version=" + (Get-Drv) + " inf=" + (Get-InfPath))

# device stuck disabled (problem 22) breaks every install op - rescue it first
$pc = Get-Prop 'DEVPKEY_Device_ProblemCode'
if ($pc -eq 22) {
  Write-Host '== device is disabled (problem 22), enabling =='
  for ($i = 1; $i -le 3 -and (Get-Prop 'DEVPKEY_Device_ProblemCode') -eq 22; $i++) {
    try { Enable-PnpDevice -InstanceId $id -Confirm:$false -ErrorAction Stop } catch { Write-Host ("  enable failed: " + $_.Exception.Message) }
    Start-Sleep -Seconds 4
  }
}

Write-Host '== step 1: stage 2015 driver into driver store =='
pnputil /add-driver $InfPath /install

if ((Get-Drv) -notlike '1030.1*') { Write-Host '== step 2: force install =='; Force2015 }

if ((Get-Drv) -notlike '1030.1*') {
  Write-Host '== step 3: remove device node, rescan, force again =='
  pnputil /remove-device "$id"
  Start-Sleep -Seconds 6
  pnputil /scan-devices
  Start-Sleep -Seconds 12
  Force2015
}

if ((Get-Drv) -notlike '1030.1*') {
  $cur = Get-InfPath
  if ($cur -and $cur -match '^oem\d+\.inf$') {
    Write-Host "== step 4: delete incumbent newer package ($cur) then force =="
    pnputil /delete-driver $cur /uninstall
    Start-Sleep -Seconds 10
    pnputil /scan-devices
    Start-Sleep -Seconds 12
    Force2015
  } else {
    Write-Host "incumbent inf is '$cur' (inbox, cannot delete) - trying force once more"
    Force2015
  }
}

if ((Get-Drv) -notlike '1030.1*') {
  Write-Host '>>> STUCK STATE (install/uninstall ops silently ignored). REBOOT Windows, then re-run this script.'
  Stop-Transcript; exit 2
}

Write-Host '== 2015 bound. Restarting device node =='
pnputil /restart-device "$id"

$T = Get-Date
Write-Host '== 60s stability watch =='
Start-Sleep -Seconds 60
Get-PnpDeviceProperty -InstanceId $id -KeyName 'DEVPKEY_Device_DriverVersion','DEVPKEY_Device_DriverDate','DEVPKEY_Device_DriverInfPath','DEVPKEY_Device_ProblemCode' | Format-Table KeyName,Data -AutoSize
$nic = Get-NetAdapter | Where-Object { $_.InterfaceDescription -like '*8812*' }
$nic | Format-List Name,Status,MacAddress
$spam = Get-WinEvent -FilterHashtable @{LogName='System'; Id=5006; StartTime=$T} -ErrorAction SilentlyContinue | Where-Object { $_.Message -match '8812' }
Write-Host ("5006 events during watch: " + @($spam).Count)

if ($nic.MacAddress -and @($spam).Count -eq 0) {
  Write-Host '>>> SUCCESS - 2015 driver stable, no reset loop.'
  if ($nic.Name) { Write-Host (">>> scan check: netsh wlan show networks interface=""" + $nic.Name + """") }
  Stop-Transcript; exit 0
} else {
  Write-Host '>>> driver installed but chip not stable - read the output above (MAC missing or 5006 spam).'
  Stop-Transcript; exit 3
}
```
