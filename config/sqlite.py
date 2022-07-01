import sqlite3

def create_db():

    conn = sqlite3.connect('database.db')

    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS `review` (
            `review_id` VARCHAR(45) NOT NULL,
            `content` VARCHAR(500) NULL DEFAULT NULL,
            `user_id` VARCHAR(45) NOT NULL,
            `place_id` VARCHAR(45) NOT NULL,
            `register_dtime` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `change_dtime` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `first_post` TINYINT(1) NOT NULL DEFAULT '0',
            `attached_photo_cnt` INT NOT NULL DEFAULT '0',
            PRIMARY KEY (`review_id`))
        '''
    )

    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS `review_photo` (
            `review_id` VARCHAR(45) NOT NULL,
            `attached_photo_id` VARCHAR(45) NOT NULL,
            `register_dtime` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        '''
    )
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS `user` (
        `user_id` VARCHAR(45) NOT NULL,
        `point` INT NOT NULL DEFAULT '0',
        `register_dtime` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`user_id`))
        '''
    )

    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS `review_log` (
            `log_no` INTEGER PRIMARY KEY AUTOINCREMENT,
            `review_id` VARCHAR(45) NOT NULL,
            `action` VARCHAR(10) NULL DEFAULT NULL,
            `content` VARCHAR(500) NULL DEFAULT NULL,
            `place_id` VARCHAR(45) NULL DEFAULT NULL,
            `user_id` VARCHAR(45) NULL DEFAULT NULL,
            `register_dtime` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `point_increment` INT(10) NULL DEFAULT '0',
            `attached_photo_ids` VARCHAR(200) NULL DEFAULT NULL)
        '''
    )
    conn.close()

    print('create db success')
