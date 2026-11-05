# Product direction / 产品方向

Chiterm should become a small, dependable project terminal for Linux: quick to learn, comfortable with several projects open, and at home on Omarchy. More code is not the goal; fewer repeated steps are.

Chiterm 的方向是一个可靠的 Linux 项目终端：容易上手，多项目并行时不混乱，并自然融入 Omarchy。衡量进展的标准是减少重复操作，而不是增加代码量。

## 1. Find what you need / 找得到功能

A searchable action palette brings existing operations, themes, and tabs into one place. Show shortcuts alongside actions so discovery also teaches keyboard use. Stable custom tab names make projects recognizable even when shell titles change.

可搜索的操作面板统一呈现操作、配色和标签，并显示快捷键。自定义标签名保持稳定，让用户不会因为 shell 改标题而找不到项目。

Acceptance: keyboard-only use, useful empty states, predictable focus, no accidental shell execution, and no stale tab targets after shells exit.

验收：全键盘操作、明确的无结果提示、正确的焦点恢复、不会执行 shell 命令、标签退出后不会留下错误目标。

## 2. Return to a project / 回到项目现场

Next, build explicitly saved workspace layouts: tab names, split orientation, relative sizes, and local directories. Restoring a layout starts fresh shells; it must not claim to restore running jobs. Missing directories need a visible fallback. Do not replay commands automatically.

下一步提供主动保存的工作区：标签名、分屏方向与比例、本地目录。恢复布局会启动新 shell，不代表恢复进程。目录失效时应明确提示并回退，不自动重放命令。

## 3. Comfortable defaults / 舒适的默认体验

Add font and scrollback preferences, a visible focused-pane treatment, and optional Omarchy palette synchronization with a fallback outside Omarchy. Keep theme, settings, and workspace persistence independently testable.

增加字体和滚动回看设置、清楚的面板焦点提示，以及可选的 Omarchy 配色同步。配色、设置和工作区保存应各自可测试，其他桌面也能正常使用。

## 4. Earn trust / 让用户放心使用

Publish real screenshots and a short workflow demo once the UI settles. Exercise fresh install, update, uninstall, and recovery from invalid settings. Publish release notes describing changes and known limits. User feedback should identify which daily tasks remain awkward before another major feature is chosen.

界面稳定后提供真实截图和简短工作流演示。持续验证首次安装、更新、卸载和异常配置恢复，并在版本说明中记录变化与限制。优先通过用户反馈确定下一项真正影响日常工作的功能。

## Success signals / 判断是否值得继续投入

- A new user can install, open two project panes, and find search without reading the full manual.
- A returning user can identify and reopen the intended project without rebuilding their layout by hand.
- Keyboard actions preserve the expected focus and never restart a running shell unexpectedly.
- Reported defects have reproducible tests; releases pass the actual GTK/VTE suite.

- 新用户不必读完整手册即可安装、打开两个项目面板并找到搜索。
- 老用户能识别并重新打开目标项目，无需手动重建布局。
- 键盘操作保持预期焦点，不会意外重启 shell。
- 用户报告的问题有可复现测试，发布版本通过真实 GTK/VTE 测试。

These are product goals, not claims about features already shipped. Workspaces and Omarchy synchronization remain planned until implemented and verified.

以上是产品目标，不表示全部已实现；工作区和 Omarchy 同步在完成实现与验收前仍属计划。
