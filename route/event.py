# -*- coding: utf-8 -
import ast
import pandas as pd
from datetime import datetime

from util.util import create_msg, check_input
from util.dao import DAO

from flask import Blueprint, request

bp = Blueprint('events', __name__, url_prefix='/events')

@bp.route('/', methods=['POST'])
def start():
    print('start')
    try:
        type = request.form['type'].upper()
        action = request.form['action'].upper()
        reviewId = request.form['reviewId']
        userId = request.form['userId']
        placeId = request.form['placeId']
    except KeyError:
        print('invalid_key')
        return create_msg(400, 'invalid_key')

    content = request.form.get('content',default='')
    attachedPhotoIds = request.form.get('attachedPhotoIds')

    if check_input(type, 'type') == False: 
        return create_msg(400, 'invalid input: input')

    if check_input(action, 'action') == False:
        return create_msg(400, 'invalid input: action')
    print('34')
    try:
        attachedPhotoIds = ast.literal_eval(attachedPhotoIds)
    except:
        return create_msg(400, 'invalid input: attachedPhotoIds')
  
    if(action == 'ADD'):
        return add_review(reviewId, userId, placeId, content, attachedPhotoIds)
    elif(action == 'MOD'):
        return mod_review(reviewId, userId, placeId, content, attachedPhotoIds)
    elif(action == 'DEL'):
        return del_review(reviewId, userId)
    
    return create_msg(500, 'failed')


def add_review(reviewId, userId, placeId, content, attachedPhotoIds):
    dao = DAO()
    print('-------ADD--------')

    # check wheather user already register the place's review
    try:
        sql = "SELECT COUNT(*) review_cnt FROM review WHERE user_id = '%s' AND place_id = '%s'"
        args = (userId, placeId)
        res, _ = dao.execute(sql, args)
    except Exception as ex:
        msg = 'db error: sql: %s, args: %s, ex: %s' % (sql, args, ex)
        print(msg)
        return create_msg(500, 'db error')
    
    if res != []:
        if res[0]['review_cnt'] > 0:
            print('review already exist')
            return create_msg(400, 'failed: duplicate review_id')
    ## 점수 계산
    score = 0
    first_post = 0
    # 1. 내용점수
    if(len(content) >= 1): score+=1
    score += len(attachedPhotoIds)
    
    # check wheather its a first review for this place
    try:
        sql = "SELECT COUNT(*) review_cnt FROM review WHERE place_id = '%s';"
        args = (placeId)

        res,_ = dao.execute(sql, args)
        print(sql)
    except Exception as ex: 
        msg = 'db error: sql: %s, args: %s, ex: %s' % (sql, args, ex)
        print(msg)
        return create_msg(500, 'db error: cannot check first review')

    if res != []:
        if res[0]['review_cnt'] in [0, '0']:
            first_post = '1'
            print('first place!')
            score += 1
    
    # add review and log
    try:
        # 회원 존재확인
        print('check user')
        sql = " SELECT * FROM user WHERE user_id = '%s';"
        args = (userId)

        res, _ = dao.execute(sql, args)
        
        if res == []:
            #  존재하지 않는 회원일 경우, 등록
            if(len(res) == 0) :
                print(len(res))
                sql = "INSERT INTO user(user_id) VALUES ('%s');"
                args = (userId)
                _, _ = dao.execute(sql, args)

        # review 등록 
        sql = "INSERT INTO review(review_id, user_id, content, place_id,\
                attached_photo_cnt, first_post)\
                VALUES ('%s', '%s', '%s', '%s', '%s', '%s');"
        args = (reviewId, userId, content, placeId, len(attachedPhotoIds), first_post)
        _, code = dao.execute(sql, args)
        if(code == 500):
            return create_msg(500, 'db error : duplicate review')


        # 사진 저장
        for attachedPhotoId in attachedPhotoIds:
            #try:
            sql = "INSERT INTO review_photo(review_id, attached_photo_id) VALUES ('%s', '%s');"
            args = (reviewId, attachedPhotoId)
            _, code = dao.execute(sql, args)
        if(code == 500):
            return create_msg(500, 'db error : failed to save photo')

        # 사진 + 첫 포스팅
        new_point = len(attachedPhotoIds) + int(first_post)
         # 고객 point 주기
        if new_point != 0:
            sql = "UPDATE user SET point = point+ '%s' WHERE user_id = '%s';"
            args = (new_point, userId)
            _, code = dao.execute(sql, args)
        if(code == 500):
            return create_msg(500, 'db error : failed to assign point')

        # log 남기기
        sql = """INSERT INTO review_log(review_id, user_id, action, content, \
            point_increment, attached_photo_ids) VALUES ("%s", "%s", "%s", "%s", "%s", "%s");"""
        args = (reviewId, userId, 'ADD', content, str(new_point), str(attachedPhotoIds))
        _, code = dao.execute(sql, args)
        if(code == 500):
            return create_msg(500, 'db error : failed to logging')

        return create_msg(200, 'success')

    except Exception as ex:
        msg = 'db error: sql: %s, args: %s, ex: %s' % (sql, args, ex)
        print(msg)
        return create_msg(500, 'db error: cannot add review')
   
    return create_msg(500, 'failed')


def mod_review(reviewId, userId, placeId, content, attachedPhotoIds):
    print('mod_review')
    dao = DAO()

    try:
        sql = "SELECT A.review_id, attached_photo_cnt, first_post, attached_photo_id \
            FROM review A, review_photo B \
            WHERE A.review_id = B.review_id and A.review_id = '%s'\
                AND A.user_id = '%s';"
        args = (reviewId, userId)
        res, _ = dao.execute(sql, args)

        if res == []:
            return create_msg(500, "failed : review does not exist")

        ex_attached_photo_cnt  = int(res[0]['attached_photo_cnt'])
        first_post = int(res[0]['first_post'])

        ex_point = ex_attached_photo_cnt + first_post
        new_point  = ex_point

        # images
        attachedPhotoIdsList = []
        for idx in range(len(res)): 
            attachedPhotoIdsList.append(res[idx]['attached_photo_id'].replace(' ', ''))

        ExPhotoDf = pd.DataFrame(data= {'id': attachedPhotoIdsList}) # before
        NewPhotoDf = pd.DataFrame(data= {'id': attachedPhotoIds}) # after
        
        if(ExPhotoDf.equals(NewPhotoDf) == False):
            #delete image
            df1 = ExPhotoDf
            df2 = NewPhotoDf
            # delete 
            df1 = df1.append(df2)
            df1 = df1.append(df2)
            set_diff_df = df1.drop_duplicates(subset=['id'],keep=False)
            # point decrease
            new_point = new_point - len(set_diff_df)

            try:
                for row in set_diff_df.itertuples():
                    sql = "DELETE FROM review_photo WHERE attached_photo_id = '%s' AND review_id = '%s';"
                    args = (row[1], reviewId) # image id, review_id
                    _, _ = dao.execute(sql, args)
            except Exception as ex:
                msg = 'db error: sql: %s, args: %s, ex: %s' % (sql, args, ex)

            #add image
            df1 = ExPhotoDf
            df2 = NewPhotoDf
            # add
            df2 = df2.append(df1)
            df2 = df2.append(df1)
            set_diff_df = df2.drop_duplicates(subset=['id'],keep=False)
            # point inrease
            new_point = new_point + len(set_diff_df)

            for row in set_diff_df.itertuples():
                sql = "INSERT INTO review_photo(review_id, attached_photo_id) VALUES ('%s', '%s');"
                args = (reviewId, row[1]) # review_id, image id
            
                _, _ = dao.execute(sql, args)
        # update review
        sql = "UPDATE review SET content = %s \
            , attached_photo_cnt = '%s' , change_dtime = '%s'\
            WHERE review_id = '%s' AND user_id = '%s' AND place_id = '%s';"
        
        args = (content, len(attachedPhotoIds), datetime.now(), 
                reviewId, userId, placeId)
        _, code = dao.execute(sql, args)
        if(code == 500):
            create_msg(500, 'db error : failed to update review')

        # user point 변경
        print('++++++++++++point!!!!!++++++++++++')
        print(ex_point)
        print(new_point)
        if(ex_point != new_point):
            sql = "UPDATE user SET point = point + '%s' WHERE user_id = '%s'"
            args = (new_point-ex_point, userId)
            print(new_point)
            _, _ = dao.execute(sql, args)

        # log 남기기
        sql = "INSERT INTO review_log(review_id, user_id, action, point_increment)\
		        VALUES ('%s', '%s', '%s', '%s');"
        args = (reviewId, userId, "MOD", str(new_point-ex_point))
        _, code = dao.execute(sql, args)
        if(code == 500):
            print('failed to logging mod!!!!!')

    except Exception as ex:
        msg = 'db error: sql: %s, args: %s, ex: %s' % (sql, args, ex)
        print(msg)
        return create_msg(500, 'db error: cannot check user place review exist\n'+ str(ex))

    return create_msg(200, 'success: mod review')


def del_review(reviewId, userId):
    print('del_review')
    # del review, photo
    dao = DAO()
    try:
        sql = "SELECT attached_photo_cnt + first_post AS point \
            FROM review WHERE review_id = '%s' AND user_id = %s;"
        args = (reviewId, userId)
        res, _ = dao.execute(sql, args)

        if res == []:
            return create_msg(500, "failed : review does not exist")
        point  = res[0]['point']

        # delete review
        sql = "DELETE FROM review WHERE review_id = '%s';"
        _, _ = dao.execute(sql, args)

        # delete photo
        sql = "DELETE FROM review_photo WHERE review_id = '%s';"
        _, _ = dao.execute(sql, args)

        # user point 회수
        sql = "UPDATE user SET point = point + '%s' WHERE user_id = '%s'"
        args = (point*-1, userId)
        _, _ = dao.execute(sql, args)

        # log 남기기
        sql = "INSERT INTO review_log(review_id, user_id, action, point_increment)\
		        VALUES ('%s', '%s', '%s', '%s');"
        args = (reviewId, userId, "DEL", point*-1)
        _, _ = dao.execute(sql, args)

    except Exception as ex:
        msg = 'db error: sql: %s, args: %s, ex: %s' % (sql, args, ex)
        print(msg)
        return create_msg(500, 'db error: cannot check user place review exist')

    return create_msg(200, 'success: delete review')
