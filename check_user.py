import os
from config import DEV_USER_ID, LEADER_ID

def admin(message):
    user_id = message.from_user.id
    admin_ids = DEV_USER_ID, LEADER_ID
    return user_id in admin_ids