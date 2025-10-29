# 三码整句输入方案

一个非常规的形码整句输入法方案。形码的离散能力一般比音码好很多，常规的形码方案通常是按四码定长设计，能够较好地将10万汉字低重地离散在26/25个按键的四维编码空间中，低重意味着确定性高选重少甚至不选重，这是形码较之音码的优势。

不过，对于汉字的日常输入需求，往往仅需要6千字不到，因此我们希望在保持日常文字输入的确定性的同时能够进一步降低码长，并且在需要的时候也可以随时且轻松地打出10万个汉字中的任何字，而形码的三码整句输入方案正是基于这样的设想构建的。

三码整句是受[墨奇五笔整句](https://github.com/gaboolic/rime-wubi-sentence)输入方案启发且改版制作的，并面向形码（特别是双编码方案，比如[宇码](https://yuhao.forfudan.com)）的特点专门做了定制性的优化，确定性有着巨大的提升，且有着更好的输入体验。


## 方案使用预览
![img](https://github.com/Litles/rime-xingma-sentence/blob/main/demo/bing_deng.png)

![img](https://github.com/Litles/rime-xingma-sentence/blob/main/demo/libaneng_baozha.png)

![img](https://github.com/Litles/rime-xingma-sentence/blob/main/demo/shisiwu_guihua.png)

![img](https://github.com/Litles/rime-xingma-sentence/blob/main/demo/yuhao_shurufa.png)

![img](https://github.com/Litles/rime-xingma-sentence/blob/main/demo/shengpizi.png)

![img](https://github.com/Litles/rime-xingma-sentence/blob/main/demo/guoqing.png)


## 方案独家特色功能

### 0.畅打十万字

可在规则统一、连贯不中断的情况下流畅地打十万汉字。虽然每个汉字的全码最多是 4 码，但日常打常用字只需要打 2、3 码打常用字，有生僻字需要时再无缝补上第 4 码即可。

![img](https://github.com/Litles/rime-xingma-sentence/blob/main/demo/sheng_pi_zi.gif)

### 1.整句句中单字选重

<img src="https://github.com/Litles/rime-xingma-sentence/blob/main/demo/dan_zi_xuan_chong.gif" width="720">

![img](https://github.com/Litles/rime-xingma-sentence/blob/main/demo/dan_zi_xuan_chong2.gif)

### 2.整句句中词选重

![img](https://github.com/Litles/rime-xingma-sentence/blob/main/demo/ci_xuan_chong.gif)

![img](https://github.com/Litles/rime-xingma-sentence/blob/main/demo/ci_xuan_chong2.gif)


## 已开发支持的形码

* **宇码·卿云(三码)** （[卿云](https://yuhao.forfudan.com/docs/joy.html)）
  * (默认)**空格版**：空格不再作为上屏键，而是像A-Z键一样被作为普通编码按键使用，这样做的好处是确定性更高、码长更短、手感更好，适合追求极致性能的人。
  * (可选)**A版**：空格是常规的上屏键，而对于两码全码的字(即字根字)，重复小码而成三码，并且不设简码，保持25键的三码输入体验，适合不喜欢打空格的人。

* **宇码·星陈(三码)** （[星陈](https://yuhao.forfudan.com/docs/#%E7%83%82%E7%84%B6%E6%98%9F%E9%99%88)）
  * (默认)**空格版**：同卿云，适合追求极致性能的人。 (两根字不需要打"回头码"，单根字是补空格而不是重复小码)
  * (可选)**A版**：同卿云，适合不喜欢打空格的人。 (两根字不需要打"回头码"，单根字重复小码成三码，有Z引导打四字以上的词)

* **天码(三码)** （[天码](https://yuhao.forfudan.com/sky)）
  * (默认)**空格版**：同卿云。 (两根字不需要打"回头码"，单根字是补空格而不是重复小码或补v)
  * (可选)**A版**：同卿云。 (两根字不需要打"回头码"，单根字重复小码成三码)

* **虎码(三码)** （[虎码](https://tiger-code.com)）
  * (默认)**空格版**：同卿云，适合追求极致性能的人。
  * (可选)**A版**：同卿云，适合不喜欢打空格的人。 (两根字不需要打"回头码"，单根字重复小码成三码)

* **新世纪五笔(三码)** （[wubi06](https://github.com/CNMan/UnicodeCJK-WuBi06)）
  * (默认)**空格版**：同卿云。
  * (可选)**A版**：同卿云。 (两根字不需要打"回头码"，单根字重复小码成三码，有Z引导打四字以上的词)

* **其他形码(比如郑码、仓颉等)**
  * 也都可以按仓库中的脚本根据常规码表一键生成相应的三码方案

> 目前方案默认使用的是知频字频表和白霜词库，如有需要也可以使用其他的替代选择，更换脚本中的文件传入参数即可；同理，由于目前默认使用的是基于简体语料库的字词频，因而较为适合简体字用户，如替换相应的词频文件亦可定制更适合繁体用户的方案。

## 三码整句使用方法

### (默认)空格版(以卿云为例)

> 空格版是指空格是不再做为上屏键，而是作为普通编码键参与输入，该方案可设一二简。优点是码长短，确定性高，手感更好

* 一简字(25个)：编码为「a_」（其中的"\_"指空格键），比如『我』"w_"
* 两码字(即字根字)：编码为「aa_」，比如『高』"dg_"
* 其他字：一律只需打前三码，比如『付』"ehc"
  * （可选）二简字(24个)：编码为「aa_」，比如『能』"dk_"
  * （可选）兼容码(三连击省第三击, 省完不足三码补v)：比如『封』"hhc", 比如『妹』"wwv"
* 若打完前三码仍然没出想打的字，可补足全码，然后补"/"
  * 三码全码字，比如『杏』"akv/"
  * 四码全码字，比如『器』"kkqk/"
  * 若补完"/"仍未出想打的字，可继续补"\_"(空格)，比如『燚』"mmmm/\_"，比如『吅』"kkv/\_\_"
* 完成整句输入后，可按「回车」或「;」上屏，也可直接打标点(比如"，。"等)顶屏

### A/Z版(以卿云为例)

> A版、Z版(A表重复小码，Z表补Z键)属于非空格版，空格是常规的上屏键，该方案也不设一二简，打一个字最少三码。优点是统一三码打字更流畅，更易提击

* 两码字(即字根字)：(A版)编码为「abb」，比如『高』"dgg"（若是Z版，该字编码将是「dgz」）
* 其他字：一律只需打前三码，比如『付』"ehc"
  * （可选）兼容码(三连击省第三击, 省完不足三码补v)：比如『封』"hhc", 比如『妹』"wwv"
* 若打完前三码仍然没出想打的字，可补足全码，然后补"/"
  * 三码全码字，比如『杏』"akv/"
  * 四码全码字，比如『器』"kkqk/"
  * 若补完"/"仍未出想打的字，可继续补"/"，比如『燚』"mmmm//"，比如『吅』"kkv///"
* 完成整句输入后，可回车上屏，也可直接打标点(比如"，。"等)顶屏

> 在输入过程中，如输入错误，可使用 Backspace 逐码回删，或使用 Tab 逐字回删

## 鸣谢

* 墨奇五笔整句 <https://github.com/gaboolic/rime-wubi-sentence>
* 白霜词库 <https://github.com/gaboolic/rime-frost>
* 宇浩输入法 <https://github.com/forFudan/yuhao>
* dyy的Rime方案 <https://github.com/happyDom/dyyRime>
