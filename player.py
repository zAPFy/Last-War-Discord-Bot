from datetime import datetime

class Player:

    def __init__(self, ctx, player_name):
        self.disc_user_id = ctx.author.id
        self.lw_user_name = player_name
        #self.lw_user_id = user_id
        self.is_blacklisted = False
        self.is_notified = False
        self.created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #self.disc_roles = ctx.author.roles
        

    def __str__(self):
        return  f"added_by: {self.disc_user_id}, " \
                f"lw_user_name: {self.lw_user_name}, " \
                f"is_blacklisted: {self.is_blacklisted}, " \
                f"is_notified: {self.is_notified}, " \
                f"created: {self.created}"
                #f"disc_role: {self.disc_role}, " \