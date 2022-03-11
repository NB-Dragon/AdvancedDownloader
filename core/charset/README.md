# Encoding And Reference
| Encoding |                                               Reference                                               |
|:--------:|:-----------------------------------------------------------------------------------------------------:|
|  UTF-8   |    [UTF-8, a transformation format of ISO 10646](http://www.rfc-editor.org/pdfrfc/rfc3629.txt.pdf)    |
|  GB2312  | [GB/T 2312-1980](http://c.gb688.cn/bzgk/gb/showGb?type=online&hcno=5664A728BD9D523DE3B99BC37AC7A2CC)  |
|   GBK    |   [汉字内码扩展规范(GBK)](https://www.ziti163.com/UploadFiles/file/20180305/6365584008556002339891497.pdf)    |
| GB18030  |  [GB 18030—2005](http://c.gb688.cn/bzgk/gb/showGb?type=online&hcno=C344D8D120B341A8DD328954A9B27A99)  |
| Unicode  |                     [Unicode® Standard](https://www.unicode.org/versions/latest)                      |
|  UTF-16  |         [UTF-16, an encoding of ISO 10646](http://www.rfc-editor.org/pdfrfc/rfc2781.txt.pdf)          |
|  UTF-32  |  [Unicode® Standard](https://www.unicode.org/versions/Unicode14.0.0/UnicodeStandard-14.0.pdf#UTF-32)  |

# Effect Comparison
## Object Definition
- Library-A: NB-Dragon/AdvancedDownloader
- Library-B: chardet/chardet[4.0.0]

## Encoding Detect Result: A
> Content: 科技兴国-怎么绿色嗘

### Result
| Encoding  | Library-A |  Library-B   |
|:---------:|:---------:|:------------:|
|   UTF-8   |   UTF-8   |    UTF-8     |
|  UTF-16   |  UTF-16   |    UTF-16    |
| UTF-16-BE | UTF-16-BE |     null     |
| UTF-16-LE | UTF-16-LE |     null     |
|  UTF-32   |  UTF-32   |    UTF-32    |
| UTF-32-BE | UTF-32-BE | Windows-1254 |
| UTF-32-LE | UTF-32-LE |     null     |

## Encoding Detect Result: B
> Content: 中奖

### Result
| Encoding | Library-A | Library-B  |
|:--------:|:---------:|:----------:|
|  GB2312  |  GB2312   | ISO-8859-1 |

## Encoding Detect Result: C
> Content: 鸡〇蛋

### Result
| Encoding | Library-A |  Library-B   |
|:--------:|:---------:|:------------:|
|   GBK    |    GBK    | Windows-1252 |

## Encoding Detect Result: D
> Content: 㐀㐀鸡〇蛋

### Result
| Encoding | Library-A | Library-B |
|:--------:|:---------:|:---------:|
| GB18030  |  GB18030  |  GB2312   |
