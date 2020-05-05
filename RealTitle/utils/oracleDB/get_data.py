from django.db.models import Q
from django.db import connection
from article.models import Article, Media, Category
import pandas as pd

# 언론사 리스트 조회
def getMediaList():
    # 언론사 리스트
    # media_list = Media.objects.raw('SELECT MEDIA_NAME FROM ARTICLE_MEDIA')
    media_list = Media.objects.values('media_name')

    return media_list

# 카테고리 리스트 조회
def getCategoryList():
    # category_list = Category.objects.raw('SELECT CATEGORY_NAME FROM ARTICLE_CATEGORY')
    category_list = Category.objects.values('category_name')
    
    return category_list

# 기사 검색 조회
def searchArticle(search_keyword, media, category):
    if search_keyword != '':
        # 언론사, 검색어 둘 다 있을 때
        if media != '':
            # article_list = Article.objects.filter(article_media = media).filter(article_title__icontains=search_keyword).order_by('-article_date')
            article_list = Article.objects.extra(select={
                                                    'media_url':'SELECT media_url FROM article_media WHERE article_article.article_media = media_name', 
                                                    'result_newtitle':'SELECT result_newtitle FROM article_result WHERE article_article.article_id = article_result.result_id',
                                                    'result_acc':'SELECT result_acc FROM article_result WHERE article_article.article_id = article_result.result_id'
                                                }).filter(article_media = media).filter(article_title__icontains=search_keyword).order_by('-article_date', 'article_id')

        # 카테고리, 검색어 둘 다 있을 때
        elif category != '':
            # article_list = Article.objects.filter(article_category = category).filter(article_title__icontains=search_keyword).order_by('-article_date')
            article_list = Article.objects.extra(select={
                                                    'media_url':'SELECT media_url FROM article_media WHERE article_article.article_media = media_name', 
                                                    'result_newtitle':'SELECT result_newtitle FROM article_result WHERE article_article.article_id = article_result.result_id',
                                                    'result_acc':'SELECT result_acc FROM article_result WHERE article_article.article_id = article_result.result_id'
                                                }).filter(article_category = category).filter(article_title__icontains=search_keyword).order_by('-article_date', 'article_id')

        # 검색어만 있을 때
        else:
            # article_list = Article.objects.filter(Q(article_title__icontains=search_keyword) | Q(article_content__icontains=search_keyword)).order_by('-article_date')
            # article_list = Article.objects.filter(article_title__icontains=search_keyword).order_by('-article_date')
            article_list = Article.objects.extra(select={
                                                    'media_url':'SELECT media_url FROM article_media WHERE article_article.article_media = media_name', 
                                                    'result_newtitle':'SELECT result_newtitle FROM article_result WHERE article_article.article_id = article_result.result_id',
                                                    'result_acc':'SELECT result_acc FROM article_result WHERE article_article.article_id = article_result.result_id'
                                                }).filter(article_title__icontains=search_keyword).order_by('-article_date', 'article_id')

    else:
        # 언론사만 있을 때
        if media != '':
            # article_list = Article.objects.filter(article_media = media).order_by('-article_date')
            article_list = Article.objects.extra(select={
                                                    'media_url':'SELECT media_url FROM article_media WHERE article_article.article_media = media_name', 
                                                    'result_newtitle':'SELECT result_newtitle FROM article_result WHERE article_article.article_id = article_result.result_id',
                                                    'result_acc':'SELECT result_acc FROM article_result WHERE article_article.article_id = article_result.result_id'
                                                }).filter(article_media = media).order_by('-article_date', 'article_id')

        # 카테고리만 있을 때
        elif category != '':
            # article_list = Article.objects.filter(article_category = category).order_by('-article_date')
            article_list = Article.objects.extra(select={
                                                    'media_url':'SELECT media_url FROM article_media WHERE article_article.article_media = media_name', 
                                                    'result_newtitle':'SELECT result_newtitle FROM article_result WHERE article_article.article_id = article_result.result_id',
                                                    'result_acc':'SELECT result_acc FROM article_result WHERE article_article.article_id = article_result.result_id'
                                                }).filter(article_category = category).order_by('-article_date', 'article_id')

        # 전체 리스트
        else:
            # article_list = Article.objects.raw('SELECT * FROM ARTICLE_ARTICLE ORDER BY ARTICLE_DATE DESC')
            # article_list = Article.objects.all().order_by('-article_date')

            # extra 사용 -> media_url 출력 안됨
            # article_list = Article.objects.extra(tables=['article_media'], where=['article_media.media_name=article_article.article_media'])
            
            # sql query 사용 -> 무한로딩..
            # article_list = Article.objects.raw('SELECT article.*, media.media_url FROM article_article article, article_media media WHERE media.media_name = article.article_media')

            article_list = Article.objects.extra(select={
                                                    'media_url':'SELECT media_url FROM article_media WHERE article_article.article_media = media_name', 
                                                    'result_newtitle':'SELECT result_newtitle FROM article_result WHERE article_article.article_id = article_result.result_id',
                                                    'result_acc':'SELECT result_acc FROM article_result WHERE article_article.article_id = article_result.result_id'
                                                }).order_by('-article_date', 'article_id')
            
    return article_list

# DB에 기사 데이터 insert
def insertArticle(file_name):
    df = pd.read_sql('select article_id from article_article group by article_id', connection)

    df.columns = ['article_id']
    df['check'] = 1

    df2 = pd.read_csv('data/' + file_name + '.csv')

    df_merge = pd.merge(df, df2, how='outer')

    df_result = df_merge[df_merge['check'].isna()]
    df_result.drop('check', axis=1, inplace=True)

    print(df_result.head())
    print(df_result.columns)
    print(df_result.shape)

    df1 = df_result[['article_id', 'article_url', 'article_category', 'article_media', 'article_date', 'article_title', 'article_content']]
    rows = [tuple(x) for x in df1.to_records(index=False)]

    for line in rows:
        # print(line)
        article_id = line[0]
        article_url = line[1]
        article_category = line[2]
        article_media = line[3]
        article_date = line[4]
        article_title = line[5]
        article_content = line[6]

        article = Article(article_id=article_id, 
                        article_url=article_url, 
                        article_category=article_category, 
                        article_media=article_media, 
                        article_date=article_date, 
                        article_title=article_title, 
                        article_content=article_content)
        article.save()

        print(article_id, 'insert complete')