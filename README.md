简单的maya流程框架(nuke, houdini还在整合)：
1. 实现基础的submite和publish功能
2. 预览资产和镜头的版本
3. 能够对接CGTeamWork（Shotgun还在整合）



## 启动：

双击/bin/$_maya_2016.bat启动，这里采用CGTeamWork数据库。

start.bat  {需要启动的软件}  {软件版本}  {项目名称}

```python
@echo off
%~sdp0\start.bat maya 2016.5 LongGongTest %*
```



## 软件配置：

打开/packages/{软件}/{版本}/info.yaml，如果需要多个版本，复制更改文件夹名字即可。

1. “env” 用来设置一些环境变量
2. ”exe“ 设置软件的安装路径
3. “tools” 设置软件的其他包

```yaml
############### Env Setup ###########################
env:
  - name: MAYA_UI_LANGUAGE
    value: en_US
    mode: over

  - name: PYTHONPATH
    value: '{XSYH_ROOT_PATH}\scripts'
    mode: prefix

  - name: MAYA_DISABLE_CLIC_IPM
    value: "1"
    mode: over

  - name: MAYA_SCRIPT_PATH
    value: "{XSYH_PACKAGE_PATH}/scripts"
    mode: prefix

## Commands for the main exe of the package.
exe: 'C:/Program Files/Autodesk/Maya2016.5/bin/maya.exe'

tools: 'C:/Program Files/Autodesk/Maya2016.5/bin/mayapy.exe'
```

打开/data/shelves/{项目}/{软件}/{版本}.yaml。根据items的数量，能够对应创建出来相应项目的 “菜单栏”。

```yaml
menu_name: MagicHill Toolkit
items:
  - type: line
    label: "line"

  - name: publisher
    label: "Open File"
    type: item
    icon: ""
    tool: open file
```



## 项目配置：

/data/config.yaml用来设置想么每个环节的 “检查项”，“命名方式”， “提交路径”， “approved 路径”等

1. "global" 片段用来设置流程软件上的字段设置，分辨率，帧速率等
2. “Model”片段即整个模型环节的配置。包括设置检查“checking_items”检查项，“提交（save_action）”时触发的一系列动作，“发布 (publisher_actions) ”触发的一系列动作。
3. 如果需要添加其他环节，按照“Model”结构复制再进行相应的调整即可。例如 “Animation”

```yaml
global:
  #--------------------------- Database Fields --------------------
  project_fields:
    - {name: entity_type, label: Entity Type, show: false,
       constant: project}
    - {name: id, label: ID, show: false}
    - {name: code, label: Code, show: true}
    - {name: status, label: Status, show: true}
    - {name: start_date, label: Start Date, show: false}
    - {name: end_date, label: End Date, show: false}

  unit: centimeter
  first_frame: 101
  fps: 24
  resolution:
    - 1920
    - 818

# --------------------- Step Config -------------------------
Model:
  work_path: '{step}_work'
  publish_path: '{step}_publish'

  submit_widget: CommentWidget
  publisher_widget: CommentWidget

  workfile_filename_description_items:
    - name: HighResolution
      short_name: high
    - name: LowResolution
      short_name: low
    - name: MidResolution
      short_name: mid
  
  workfile_save_actions:
    - name: workfile_root
      type: GetPathFromTag
      parms:
        input: '{step}_work'
        output: 'None'

    - type: DeleteUnknown

    - type: SaveAsScene
      parms:
        input: '{workfile_root}/{GetFilename}'
    
  publisher_actions:
    - type: SetLowViwer
      parms:
        wireframe: true

    - type: SaveScene
      parms:
        format: 'mb'
        
# --------------------- Step Config -------------------------
Animation:
  short_name: Ani
  work_path: '{step}_work'
  publish_path: '{step}_publish'

  submit_widget: CommentWidget
  publisher_widget: CommentWidget

  checking_items:
    - name: checkCGtFrame
      must: 0
    - name: changeAniFrame
      must: 0
    - name: CheckCamera
      must: 0
```



## 待补充
