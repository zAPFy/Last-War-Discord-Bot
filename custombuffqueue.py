from queue import Queue
from custombuffqueuetypes import CustomBuffQueueTypes
from datetime import datetime, timedelta
from player import Player

class CustomBuffQueue(Queue):
    """
    This is a sample class.
    """

    def __init__(self, type:CustomBuffQueueTypes, maxsize: int=100):
        self.type=type
        self.description=None
        self.created=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.last_popped=datetime.now()
        super().__init__(maxsize)


    def put(self, player:Player, block=True, timeout=None):
        """
        This function implements a custom put used for input validation und duplicate preventio.

        Parameters:
        target_name (string): Last War username of the player who's position needs to be known.

        Returns:
        int: Current position in the buff queue (Starting from 0).
        """
        if not isinstance(player, Player):
            raise ValueError("Only instances of Player class can be added to CustomBuffQueue")
        
        if self.get_position(player.lw_user_name) >= 0:
            raise Exception("Player with identical username is already enqueued.")

        super().put(player, block, timeout)


    def get_item(self, target_name: str):
        """
        This function returns the player instance item of specified user name in the buff queue.

        Parameters:
        target_name (string): Last War username of the player who's position needs to be known.

        Returns:
        Player: Player instance with specified name.
        """
        print("Trying to get queue position of player with username '" + str(target_name) + "'.")
        is_found=False

        # Create a copy of the queue to preserve its contents
        temp_queue=Queue(maxsize=self.maxsize)

        while not self.empty():
            player=self.get()
            temp_queue.put(player)  # Put the player back into the original queue after checking
            if player.lw_user_name == target_name:
                is_found=True
                break
        
        # Restore the original queue
        while not temp_queue.empty():
            self.put(temp_queue.get())

        return player
        

    def get_position(self, target_name: str):
        """
        This function returns the position of specified user name in the buff queue.

        Parameters:
        target_name (string): Last War username of the player who's position needs to be known.

        Returns:
        int: Current position in the buff queue (Starting from 0).
        """

        print("Trying to get queue position of player with username '" + str(target_name) + "'.")
        position=0
        is_found=False

        # Create a copy of the queue to preserve its contents
        temp_queue=Queue(maxsize=self.maxsize)

        while not self.empty():
            player=self.get()
            temp_queue.put(player)  # Put the player back into the original queue after checking
            if player.lw_user_name == target_name:
                is_found=True
                break
            position += 1
        
        # Restore the original queue
        while not temp_queue.empty():
            self.put(temp_queue.get())

        if is_found:
            return position
        else:
            return -1  # Return -1 if the target_name player is not is_found in the queue


    def remove(self, target_name:str):
        """
        This function removes the specified user name from the buff queue.

        Parameters:
        target_name (string): Last War username of the player to be removed.

        Returns:
        type: Description of the return value.
        """

        print("Trying to remove player with username '" + str(target_name) + "' from queue.")
        count=0
        temp_queue=Queue(maxsize=self.maxsize)

        # Dequeue players from the original queue and enqueue them into a temporary queue,
        # except for the player to be removed
        while not self.empty():
            player=self.get()
            if player.lw_user_name != target_name:
                temp_queue.put(player)
            else:
                count += 1

        # Dequeue players from the temporary queue and enqueue them back into the original queue
        while not temp_queue.empty():
            self.put(temp_queue.get())
        
        return count >= 1
    

    def list(self):
        """
        This function lists all players in the buff queue.

        Returns:
        list: A list of dictionaries containing information about each player.
        """
        queue_list=[]
        count = 0

        # Create a copy of the queue to preserve its contents
        temp_queue=Queue(maxsize=self.maxsize)

        while not self.empty():
            player=self.get()
            temp_queue.put(player)  # Put the player back into the original queue after processing

            print(f"Player {count + 1}: {player.lw_user_name} (Added by: {player.disc_user_id})")
            
            player_info={
                "position": count,                  # Position in the queue
                "player":   player.lw_user_name,
                "added by": player.disc_user_id
            }
            queue_list.append(player_info)
            count += 1

        # Restore the original queue
        while not temp_queue.empty():
            self.put(temp_queue.get())

        return queue_list


    def estimate_start_time(self, position: int):
        """
        This function calculates the estimated starting time for the nth player in the buff queue.

        Returns:
        datetime: Estimated starting time (server time + position + 3 minutes buffer).
        """
        waiting_time = timedelta(minutes=10 * position + 3)

        start_time = self.last_popped + waiting_time

        return start_time


    def __str__(self):
        """
        This dunder function prints the custom buff queue.

        Parameters:
        -

        Returns:
        str: Description of the return value.
        """
        return  f"Type: {self.type}, " \
                f"Description: {self.description}, " \
                f"Created: {self.created}, " \
                f"Maxsize: {self.maxsize}", \
                f"Last Time Popped: {self.last_popped}"