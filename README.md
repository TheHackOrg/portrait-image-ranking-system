## Intro
A portrait image ranking system, used Python3.12.3, Flask3.0.3 and SQLite3.39.5

Thanks for ELO rating algorithm :
* $P(D) = \frac{1}{2} + \int_{0}^{D}{\frac{1}{\sqrt{2\pi}\sigma}e^{\frac{-x^2}{2\sigma^2}}dx}$, that's equal with the formula of $P(D) = \frac{1}{1 + 10^{\frac{D}{400}}}$, and be used to calculate the expected value of win
* $R_n = R_o + K * (W - P(D))$, which be used to calculate the new ranking score


## Screenshot
![index.html](https://gitee.com/hackorg/portrait-image-ranking-system/raw/master/screenshot/index.html.png)


## How to use it
1. Install the project dependency.
```shell
pip3 install -r requirements.txt
```

2. Create database tables, and the default database name is `portrait_image.db`.
```python
class SQLite3DB:
    DATABASE_NAME = 'portrait_image.db'
```
```python
class SQLite3DBTest:
    SQLite3DB.create_table()
```

3. Store the all images of specifical folder into database, but before that, maybe you need to change the default image path.
```python
class ImageTool:
    PORTRAIT_IMG_FOLDER = '/portrait_img_folder'
```
```python
class SQLite3DBTest:
    SQLite3DB.store_img_into_db()
```

4. Modify the default initial ranking of ELO ranking algorithm if you need, that according to the scale of the competition, etc.
```python
DEFAULT_RANKING = 1400
```

5. Run it, Have fun with it bro.
```python
class WebControllerTest:
    WebController.app.run(host='0.0.0.0', port=80, debug=True)
```
```shell
python3 portrait_image_ranking_system.py
```


## Question
There have two questions for you, maybe it's help you to understand the advantage and principle of ELO rating algorithm, and you can get answer in blogs of reference part.

* Why do we use ELO instead of a traditional points-based system ?
* What's the formula meaning of $P(D) = \frac{1}{2} + \int_{0}^{D}{\frac{1}{\sqrt{2\pi}\sigma}e^{\frac{-x^2}{2\sigma^2}}dx}$ ?


## Reference
* [ELO Wiki](https://en.m.wikipedia.org/wiki/Elo_rating_system)
* [有趣的 Elo 积分系统](https://wangwei1237.github.io/2023/08/12/the-interesting-elo-rating-system/)
* [ELO积分算法](https://zhuanlan.zhihu.com/p/46491630)
* [电影<<社交网络>>中的"FaceMash"算法](https://sylvanassun.github.io/2017/07/19/2017-07-19-FaceMash/)