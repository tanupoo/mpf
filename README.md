Multipurpose Filter
===================

## MIME decode

```
% maildecode.py -h
usage: maildecode.py [-h] [-x DECODE] [-o OUT_FILE] [mail_file]

mail decoder.

positional arguments:
  mail_file    specify a filename.

options:
  -h, --help   show this help message and exit
  -x DECODE    specify the number of the content to be decoded. if 0, it
               shows the header.
  -o OUT_FILE  specify the name to save data in case when the content type is
               image.
```

## URL decode/encode

```
% urlencode.py 'https://www.google.com/search?client=firefox-b-d&q=+ほげ'
https://www.google.com/search?client=firefox-b-d&q=%2B%E3%81%BB%E3%81%92
```

```
% urldecode.py 'https://www.google.com/search?client=firefox-b-d&q=%2B%E3%81%BB%E3%81%92'
https://www.google.com/search?client=firefox-b-d&q=+ほげ
```

## quoted-print decode/encode

```
% cat text.txt | qpencode.py -n
=E6=97=A5=E6=9C=AC=E3=81=AE=E3=81=BF=E3=81=A7=E4=BD=BF=E7=94=A8=E3=81=95=E3=
=82=8C=E3=82=8B=E3=83=A1=E3=82=BF=E6=A7=8B=E6=96=87=E5=A4=89=E6=95=B0=E3=81=
=A8=E3=81=97=E3=81=A6
=E3=80=8Choge=EF=BC=88=E3=81=BB=E3=81=92[2]=EF=BC=89=E3=80=8D
=E3=80=8Cfuga=EF=BC=88=E3=81=B5=E3=81=8C=EF=BC=89=E3=80=8D
=E3=80=8Cpiyo=EF=BC=88=E3=81=B4=E3=82=88=EF=BC=89=E3=80=8D
=E3=80=8Chogera=EF=BC=88=E3=81=BB=E3=81=92=E3=82=89=EF=BC=89=E3=80=8D
=E3=80=8Chogehoge=EF=BC=88=E3=81=BB=E3=81=92=E3=81=BB=E3=81=92=EF=BC=89=E3=
=80=8D
=E3=81=AA=E3=81=A9=E3=81=8C=E3=81=82=E3=82=8B=E3=80=82=20
```

```
% cat text.txt | qpencode.py -n | qpdecode.py -n
日本のみで使用されるメタ構文変数として
「hoge（ほげ[2]）」
「fuga（ふが）」
「piyo（ぴよ）」
「hogera（ほげら）」
「hogehoge（ほげほげ）」
などがある。 
```
