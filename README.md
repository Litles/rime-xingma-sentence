# 三码整句输入方案

一个非常规的形码整句输入法方案。形码的离散能力一般比音码好很多，常规的形码方案通常是按四码定长设计，能够较好地将10万汉字低重地离散在26/25个按键的四维编码空间中，低重意味着确定性高选重少甚至不选重，这是形码较之音码的优势。

不过，对于汉字的日常输入需求，往往仅需要6千字不到，因此我们希望在保持日常文字输入的确定性的同时能够进一步降低码长，并且在需要的时候也可以随时且轻松地打出10万个汉字中的任何字，而形码的三码整句输入方案正是基于这样的设想构建的。

三码整句是受[墨奇五笔整句](https://github.com/gaboolic/rime-wubi-sentence)输入方案启发且改版制作的，并面向形码（特别是双编码方案，比如[宇码](https://yuhao.forfudan.com)）的特点专门做了定制性的优化，确定性有着巨大的提升，且有着更好的输入体验。


## 方案使用预览
![img](https://github.com/Litles/rime-xingma-sentence/blob/main/images/bing_deng.png)

![img](https://github.com/Litles/rime-xingma-sentence/blob/main/images/libaneng_baozha.png)

![img](https://github.com/Litles/rime-xingma-sentence/blob/main/images/shisiwu_guihua.png)

![img](https://github.com/Litles/rime-xingma-sentence/blob/main/images/shengpizi.png)


## 已开发支持的形码

* **宇码·卿云(三码)**
  * (默认)**空格版**：空格不再作为上屏键，而是像A-Z键一样被作为普通编码按键使用，这样做的好处是确定性更高、码长更短、手感更好。
  * (可选)**Z版**：空格是常规的上屏键，而对于两码全码的字(即字根字)，补加Z键而成三码，并且不设简码，保持25键的三码输入体验。

* **宇码·星陈(三码)**
  * (默认)**空格版**：同卿云。(并且由于按卿云一样的思路设计，不再需要打"回头码"，两码字是补空格而不是重复小码)
  * (可选)**Z版**：同卿云。(并且由于按卿云一样的思路设计，不再需要打"回头码"，两码字是补Z键而不是重复小码)

* **其他形码(比如五笔、郑码等)**也都可以按仓库中的脚本根据常规码表一键生成相应的三码方案

> 目前方案默认使用的是知频字频表和白霜词库，如有需要也可以使用其他的替代选择，更换脚本中的文件传入参数即可；同理，由于目前默认使用的是基于简体语料库的字词频，因而较为适合简体字用户，如替换相应的词频文件亦可定制更适合繁体用户的方案。

## 鸣谢

* 墨奇五笔整句 <https://github.com/gaboolic/rime-wubi-sentence>
* 白霜词库 <https://github.com/gaboolic/rime-frost>
* 宇浩输入法 <https://github.com/forFudan/yuhao>
