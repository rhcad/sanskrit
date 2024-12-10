# sanskrit-study

梵语（读音、天城体、转写）学习

[在线页面](http://ggbstudy.top/sa/)

## 文件说明

- `./utils`: 制作用的通用脚本
- `./lrc_mp3`: 内部制作数据文件，含歌词、原始音频
- `./mp3`: HTML用的词句音频文件
- `./script`: HTML用的脚本和样式文件
- `./*.htm`: 最终HTML

## 制作

- 安装 Python 3.8+ 和依赖库
  - `pip install -r requirements.txt`
  - 使用音频库pydub、歌词库pylrc、ffmpeg工具

- 如果原始音视频不是mp3，可用 `utils/audio2mp3.py` 转换，需安装 `ffmpeg`

- mp3转lrc歌词文件
  - 从无背景音乐的 mp3 文件根据静音识别自动拆分出词mp3文件、lrc歌词文件（有lrc则跳过本步骤）
    - 运行 `utils/mp3_to_lrc.py` 从读诵 mp3 文件拆分出词mp3文件（仅对照用）、lrc歌词文件
    - 对照词mp3文件修改lrc歌词文件
      - 如果是词，就将`] `后的文本改为 iast转写文本
      - 如果连续几个mp3对应一个词，就删除多余的行，执行上一步改写操作
    - 在lrc歌词文件特定行末尾加上标点 `, | ||`，以便下一步能拆句

  - 如果mp3有背景音乐，或已有初步lrc文件，可用 [歌词滚动姬](https://lrc-maker.github.io/3.x/) 在线编辑
    - 加载文本：根据IAST内容结构先拆分出所有lrc内容行，行末可加标点 `, | ||`
    - 加载音频，切换到“打轴”页面开始播放，在每行开始时刻按空格键记录时刻

- 从原始 mp3 文件、lrc歌词文件生成词和句的音频文件
  - 将 mp3、lrc 放在同一个目录，改为相同的文件名（后缀名保留）
  - 运行 `lrc_mp3/split_mp3.py` 或 `utils/split_mp3.py`，生成词和句的音频文件
  - 将生成的 txt 文件内容复制到根目录下的网页文件中 `iastContent = ...`，指定mp3路径

## 运行

打开根目录下的网页文件验证
- IAST、天城体转换使用了开源库 `script/sanscript.es6.js`

## 欢迎改进

本项目采用MIT开源许可，您可参与改进或改编使用，可提 issue 讨论。
