from tkinter import *
import time
import copy
import numpy
import pickle
import neat
import predictor


class Checker:
    def __init__(self, position, identity, color, player, checkerboard):
        self.player = player
        self.id = identity
        self.is_king = False
        self.can_eat = False
        self.position = position
        self.can_move = True
        self.checkerboard = checkerboard

        if player == 1:
            self.opponent = 2
        else:
            self.opponent = 1

        x_position = checkerboard.position_table_x[position[0]]
        y_position = checkerboard.position_table_y[position[1]]
        checkerboard.canvas.create_oval(x_position - 90, y_position - 90, x_position - 10, y_position - 10, fill=color,
                                        tag=identity)

    def get_id(self):
        return self.id

    def get_position(self):
        return self.position

    def get_player(self):
        return self.player

    def get_can_move(self):
        return self.can_move

    def get_opponent(self):
        return self.opponent

    def get_can_eat(self):
        return self.can_eat

    def move_to(self, new_position):
        self.checkerboard.click_safe = False

        current_coordinates = self.checkerboard.canvas.coords(self.id)
        new_x = self.checkerboard.position_table_x[new_position[0]]
        new_y = self.checkerboard.position_table_y[new_position[1]]
        x_direction = new_x - current_coordinates[2]
        y_direction = new_y - current_coordinates[3]

        if x_direction < 0 and y_direction < 0:
            while current_coordinates[2] != new_x - 10 and current_coordinates[3] != new_y - 10:
                self.checkerboard.canvas.move(self.id, -1, -1)
                self.checkerboard.window.update()
                time.sleep(self.checkerboard.movement_time)
                current_coordinates = self.checkerboard.canvas.coords(self.id)

        if x_direction < 0 < y_direction:
            while current_coordinates[2] != new_x - 10 and current_coordinates[3] != new_y - 10:
                self.checkerboard.canvas.move(self.id, -1, 1)
                self.checkerboard.window.update()
                time.sleep(self.checkerboard.movement_time)
                current_coordinates = self.checkerboard.canvas.coords(self.id)

        if x_direction > 0 > y_direction:
            while current_coordinates[2] != new_x - 10 and current_coordinates[3] != new_y - 10:
                self.checkerboard.canvas.move(self.id, 1, -1)
                self.checkerboard.window.update()
                time.sleep(self.checkerboard.movement_time)
                current_coordinates = self.checkerboard.canvas.coords(self.id)

        if x_direction > 0 and y_direction > 0:
            while current_coordinates[2] != new_x - 10 and current_coordinates[3] != new_y - 10:
                self.checkerboard.canvas.move(self.id, 1, 1)
                self.checkerboard.window.update()
                time.sleep(self.checkerboard.movement_time)
                current_coordinates = self.checkerboard.canvas.coords(self.id)

        self.position = new_position

        if self.player == 1 and not self.is_king:
            new_position_y = int(new_position[1])
            if new_position_y == 8:
                self.make_king()

        if self.player == 2 and not self.is_king:
            new_position_y = int(new_position[1])
            if new_position_y == 1:
                self.make_king()

        self.checkerboard.click_safe = True

    def make_king(self):
        x = self.checkerboard.position_table_x[self.position[0]]
        y = self.checkerboard.position_table_y[self.position[1]]

        self.checkerboard.canvas.create_text(x - 50, y - 50, text="KING", fill="black", tag=self.id,
                                             font=("Purisa", 20))
        self.is_king = True

    def set_can_eat(self):
        self.can_eat = False
        current_x = ord(self.position[0])
        current_y = int(self.position[1])

        if self.player == 1 or self.is_king:
            right_front_x = current_x + 1
            right_front_y = current_y + 1
            right_landing_x = right_front_x + 1
            right_landing_y = right_front_y + 1

            left_front_x = current_x - 1
            left_front_y = current_y + 1
            left_landing_x = left_front_x - 1
            left_landing_y = left_front_y + 1

            if right_landing_x < 105 and right_landing_y < 9:
                right_front = [str(chr(right_front_x)), str(right_front_y)]
                right_landing = [str(chr(right_landing_x)), str(right_landing_y)]

                possibly_eaten_checker = self.checkerboard.search_by_position(right_front, self.opponent)
                landing_space_player = self.checkerboard.search_by_position(right_landing, self.player)
                landing_space_opponent = self.checkerboard.search_by_position(right_landing, self.opponent)

                if possibly_eaten_checker is not None and landing_space_player is None \
                        and landing_space_opponent is None:
                    self.can_eat = True

            if left_landing_x > 96 and left_landing_y < 9:
                left_front = [str(chr(left_front_x)), str(left_front_y)]
                left_landing = [str(chr(left_landing_x)), str(left_landing_y)]

                possibly_eaten_checker = self.checkerboard.search_by_position(left_front, self.opponent)
                landing_space_player = self.checkerboard.search_by_position(left_landing, self.player)
                landing_space_opponent = self.checkerboard.search_by_position(left_landing, self.opponent)

                if possibly_eaten_checker is not None and landing_space_player is None \
                        and landing_space_opponent is None:
                    self.can_eat = True

        if self.player == 2 or self.is_king:
            right_front_x = current_x + 1
            right_front_y = current_y - 1
            right_landing_x = right_front_x + 1
            right_landing_y = right_front_y - 1

            left_front_x = current_x - 1
            left_front_y = current_y - 1
            left_landing_x = left_front_x - 1
            left_landing_y = left_front_y - 1

            if right_landing_x < 105 and right_landing_y > 0:
                right_front = [str(chr(right_front_x)), str(right_front_y)]
                right_landing = [str(chr(right_landing_x)), str(right_landing_y)]

                possibly_eaten_checker = self.checkerboard.search_by_position(right_front, self.opponent)
                landing_space_player = self.checkerboard.search_by_position(right_landing, self.player)
                landing_space_opponent = self.checkerboard.search_by_position(right_landing, self.opponent)

                if possibly_eaten_checker is not None and landing_space_player is None \
                        and landing_space_opponent is None:
                    self.can_eat = True

            if left_landing_x > 96 and left_landing_y > 0:
                left_front = [str(chr(left_front_x)), str(left_front_y)]
                left_landing = [str(chr(left_landing_x)), str(left_landing_y)]

                possibly_eaten_checker = self.checkerboard.search_by_position(left_front, self.opponent)
                landing_space_player = self.checkerboard.search_by_position(left_landing, self.player)
                landing_space_opponent = self.checkerboard.search_by_position(left_landing, self.opponent)

                if possibly_eaten_checker is not None and landing_space_player is None \
                        and landing_space_opponent is None:
                    self.can_eat = True

    def find_all_can_eat(self, can_move, right_front_x, right_front_y, right_landing_x, right_landing_y,
                         left_front_x, left_front_y, left_landing_x, left_landing_y, step, direction):

        if direction == 1:
            current_position = [str(chr(right_front_x - 1)), str(right_front_y - 1)]
        else:
            current_position = [str(chr(right_front_x - 1)), str(right_front_y + 1)]

        right_front = [str(chr(right_front_x)), str(right_front_y)]
        right_landing = [str(chr(right_landing_x)), str(right_landing_y)]
        left_front = [str(chr(left_front_x)), str(left_front_y)]
        left_landing = [str(chr(left_landing_x)), str(left_landing_y)]

        right_checker = self.checkerboard.search_by_position(right_front, self.opponent)
        left_checker = self.checkerboard.search_by_position(left_front, self.opponent)

        right_friendly = self.checkerboard.search_by_position(right_front, self.player)
        left_friendly = self.checkerboard.search_by_position(left_front, self.player)

        if self.is_king and step:
            if direction == 1:
                right_back = [str(chr(left_front_x + 2)), str(left_front_y - 2)]
                right_back_landing = [str(chr(left_front_x + 3)), str(left_front_y - 3)]
                left_back = [str(chr(right_front_x - 2)), str(right_front_y - 2)]
                left_back_landing = [str(chr(right_front_x - 3)), str(right_front_y - 3)]

            else:
                right_back = [str(chr(left_front_x + 2)), str(left_front_y + 2)]
                right_back_landing = [str(chr(left_front_x + 3)), str(left_front_y + 3)]
                left_back = [str(chr(right_front_x - 2)), str(right_front_y + 2)]
                left_back_landing = [str(chr(right_front_x - 3)), str(right_front_y + 3)]

            right_back_checker = self.checkerboard.search_by_position(right_back, self.opponent)
            left_back_checker = self.checkerboard.search_by_position(left_back, self.opponent)

            if right_back_checker is not None and (left_front_x + 3) < 105 and 9 > int(right_back_landing[1]) > 0 \
                    and (len(can_move) == 0 or [right_back_landing, current_position] not in can_move) and \
                            [current_position, right_back_landing] not in can_move:
                landing_player = self.checkerboard.search_by_position(right_back_landing, self.player)
                landing_opponent = self.checkerboard.search_by_position(right_back_landing, self.opponent)
                if (landing_player is None and landing_opponent is None) or \
                        (right_back_landing == self.get_position() and landing_player is not None and step):
                    can_move.append([current_position, right_back_landing])

                    if direction == 1:
                        if left_front_y - 4 > 0:
                            self.find_all_can_eat(can_move, ord(right_back_landing[0]) + 1,
                                                  int(right_back_landing[1]) - 1,
                                                  ord(right_back_landing[0]) + 2, int(right_back_landing[1]) - 2,
                                                  ord(right_back_landing[0]) - 1, int(right_back_landing[1]) - 1,
                                                  ord(right_back_landing[0]) - 2, int(right_back_landing[1]) - 2, True,
                                                  2)

                    if direction == 2:
                        if left_front_y + 4 < 9:
                            self.find_all_can_eat(can_move, ord(right_back_landing[0]) + 1,
                                                  int(right_back_landing[1]) + 1,
                                                  ord(right_back_landing[0]) + 2, int(right_back_landing[1]) + 2,
                                                  ord(right_back_landing[0]) - 1, int(right_back_landing[1]) + 1,
                                                  ord(right_back_landing[0]) - 2, int(right_back_landing[1]) + 2, True,
                                                  1)

            if left_back_checker is not None and (right_front_x - 3) > 96 and 9 > int(left_back_landing[1]) > 0 \
                    and (len(can_move) == 0 or [left_back_landing, current_position] not in can_move) and \
                            [current_position, left_back_landing] not in can_move:
                landing_player = self.checkerboard.search_by_position(left_back_landing, self.player)
                landing_opponent = self.checkerboard.search_by_position(left_back_landing, self.opponent)

                if landing_player is None and landing_opponent is None or \
                        (left_back_landing == self.get_position() and landing_player is not None and step):
                    can_move.append([current_position, left_back_landing])

                    if direction == 1:
                        if right_front_y - 4 > 0:
                            self.find_all_can_eat(can_move, ord(left_back_landing[0]) + 1,
                                                  int(left_back_landing[1]) - 1,
                                                  ord(left_back_landing[0]) + 2, int(left_back_landing[1]) - 2,
                                                  ord(left_back_landing[0]) - 1, int(left_back_landing[1]) - 1,
                                                  ord(left_back_landing[0]) - 2, int(left_back_landing[1]) - 2, True,
                                                  2)

                    if direction == 2:
                        if right_front_y + 4 < 9:
                            self.find_all_can_eat(can_move, ord(left_back_landing[0]) + 1,
                                                  int(left_back_landing[1]) + 1,
                                                  ord(left_back_landing[0]) + 2, int(left_back_landing[1]) + 2,
                                                  ord(left_back_landing[0]) - 1, int(left_back_landing[1]) + 1,
                                                  ord(left_back_landing[0]) - 2, int(left_back_landing[1]) + 2, True,
                                                  1)

        if right_checker is None and left_checker is None and right_friendly is None and left_friendly is None:
            if not step:
                if right_front_x < 105:
                    can_move.append([self.position, right_front])

                if left_front_x > 96:
                    can_move.append([self.position, left_front])
                return

            return

        if right_checker is None and right_friendly is None and not step:
            can_move.append([self.position, right_front])

        if left_checker is None and left_friendly is None and not step:
            can_move.append([self.position, left_front])

        if right_checker is not None and right_landing_x < 105 and 9 > right_landing_y > 0 \
                and (len(can_move) == 0 or [right_landing, current_position] not in can_move) and \
                        [current_position, right_landing] not in can_move:  # will never be more that 0
            landing_space_player = self.checkerboard.search_by_position(right_landing, self.player)
            # if checker is player 1
            landing_space_opponent = self.checkerboard.search_by_position(right_landing, self.opponent)

            if landing_space_player is None and landing_space_opponent is None or \
                    (right_landing == self.get_position() and landing_space_player is not None and step):
                can_move.append([current_position, right_landing])

                if direction == 1:
                    if right_landing_y + 1 < 9:
                        self.find_all_can_eat(can_move, right_landing_x + 1, right_landing_y + 1, right_landing_x + 2,
                                              right_landing_y + 2, right_landing_x - 1, right_landing_y + 1,
                                              right_landing_x - 2, right_landing_y + 2, True, 1)

                if direction == 2:
                    if right_landing_y - 1 > 0:
                        self.find_all_can_eat(can_move, right_landing_x + 1, right_landing_y - 1,
                                              right_landing_x + 2,
                                              right_landing_y - 2, right_landing_x - 1, right_landing_y - 1,
                                              right_landing_x - 2, right_landing_y - 2, True, 2)

        if left_checker is not None and left_landing_x > 96 and 9 > left_landing_y > 0 \
                and (len(can_move) == 0 or [left_landing, current_position] not in can_move) and \
                        [current_position, left_landing] not in can_move:
            landing_space_player = self.checkerboard.search_by_position(left_landing, self.player)
            landing_space_opponent = self.checkerboard.search_by_position(left_landing, self.opponent)

            if landing_space_player is None and landing_space_opponent is None or \
                    (left_landing == self.get_position() and landing_space_player is not None and step):
                can_move.append([current_position, left_landing])

                if direction == 1:
                    if left_landing_y + 1 < 9:
                        self.find_all_can_eat(can_move, left_landing_x + 1, left_landing_y + 1, left_landing_x + 2,
                                              left_landing_y + 2, left_landing_x - 1, left_landing_y + 1,
                                              left_landing_x - 2,
                                              left_landing_y + 2, True, 1)

                if direction == 2:
                    if left_landing_y - 1 > 0:
                        self.find_all_can_eat(can_move, left_landing_x + 1, left_landing_y - 1, left_landing_x + 2,
                                              left_landing_y - 2, left_landing_x - 1, left_landing_y - 1,
                                              left_landing_x - 2,
                                              left_landing_y - 2, True, 2)

        return

    def get_movements(self):
        can_move = []
        current_x = ord(self.position[0])
        current_y = int(self.position[1])

        if self.player == 1 or self.is_king:
            right_front_x = current_x + 1
            right_front_y = current_y + 1
            right_landing_x = right_front_x + 1
            right_landing_y = right_front_y + 1

            left_front_x = current_x - 1
            left_front_y = current_y + 1
            left_landing_x = left_front_x - 1
            left_landing_y = left_front_y + 1

            if (right_front_x < 105 and right_front_y < 9) or (left_front_x > 96 and left_front_y < 9):
                #  Because Movement in one direction is possible therefore must be OR and movements stop at 8 for pawns.
                self.find_all_can_eat(can_move, right_front_x, right_front_y, right_landing_x,
                                      right_landing_y,
                                      left_front_x, left_front_y, left_landing_x, left_landing_y, False, 1)

        if self.player == 2 or self.is_king:
            right_front_x = current_x + 1
            right_front_y = current_y - 1
            right_landing_x = right_front_x + 1
            right_landing_y = right_front_y - 1

            left_front_x = current_x - 1
            left_front_y = current_y - 1
            left_landing_x = left_front_x - 1
            left_landing_y = left_front_y - 1

            if (right_front_x < 105 and right_front_y > 0) or (left_front_x > 96 and left_front_y > 0):
                self.find_all_can_eat(can_move, right_front_x, right_front_y, right_landing_x,
                                      right_landing_y,
                                      left_front_x, left_front_y, left_landing_x, left_landing_y, False, 2)

        return can_move

    def movable(self):
        current_x = ord(self.position[0])
        current_y = int(self.position[1])
        self.set_can_eat()
        movable_front = True
        movable_back = True

        if self.player == 1 or self.is_king:
            right_front_x = current_x + 1
            right_front_y = current_y + 1
            left_front_x = current_x - 1
            left_front_y = current_y + 1

            right_front = [str(chr(right_front_x)), str(right_front_y)]
            left_front = [str(chr(left_front_x)), str(left_front_y)]

            if current_y + 1 >= 9:
                self.can_move = False
                movable_front = False

            if right_front_x >= 105 and not self.can_eat:
                left = self.checkerboard.search_by_position(left_front, self.player)
                left_friendly = self.checkerboard.search_by_position(left_front, self.opponent)
                if left is not None or left_friendly is not None:
                    self.can_move = False
                    movable_front = False

            if left_front_x <= 96 and not self.can_eat:
                right = self.checkerboard.search_by_position(right_front, self.player)
                right_friendly = self.checkerboard.search_by_position(right_front, self.opponent)
                if right is not None or right_friendly is not None:
                    self.can_move = False
                    movable_front = False

            if not self.can_eat:
                right = self.checkerboard.search_by_position(right_front, self.player)
                right_friendly = self.checkerboard.search_by_position(right_front, self.opponent)
                if right is not None or right_friendly is not None:
                    left = self.checkerboard.search_by_position(left_front, self.player)
                    left_friendly = self.checkerboard.search_by_position(left_front, self.opponent)
                    if left is not None or left_friendly is not None:
                        self.can_move = False
                        movable_front = False

        if self.player == 2 or self.is_king:
            right_front_x = current_x + 1
            right_front_y = current_y - 1
            left_front_x = current_x - 1
            left_front_y = current_y - 1

            right_front = [str(chr(right_front_x)), str(right_front_y)]
            left_front = [str(chr(left_front_x)), str(left_front_y)]

            if current_y - 1 <= 0:
                self.can_move = False
                movable_back = False

            if right_front_x >= 105 and not self.can_eat:
                left = self.checkerboard.search_by_position(left_front, self.player)
                left_friendly = self.checkerboard.search_by_position(left_front, self.opponent)
                if left is not None or left_friendly is not None:
                    self.can_move = False
                    movable_back = False

            if left_front_x <= 96 and not self.can_eat:
                right = self.checkerboard.search_by_position(right_front, self.player)
                right_friendly = self.checkerboard.search_by_position(right_front, self.opponent)
                if right is not None or right_friendly is not None:
                    self.can_move = False
                    movable_back = False

            if not self.can_eat:
                right = self.checkerboard.search_by_position(right_front, self.player)
                right_friendly = self.checkerboard.search_by_position(right_front, self.opponent)
                if right is not None or right_friendly is not None:
                    left = self.checkerboard.search_by_position(left_front, self.player)
                    left_friendly = self.checkerboard.search_by_position(left_front, self.opponent)
                    if left is not None or left_friendly is not None:
                        self.can_move = False
                        movable_back = False

        if self.player == 1 and not self.is_king:
            if movable_front:
                self.can_move = True

        if self.player == 2 and not self.is_king:
            if movable_back:
                self.can_move = True

        if self.is_king:
            if movable_front or movable_back:
                self.can_move = True

    @staticmethod
    def has_next_movement(movement_array, current_position):
        for index, movement in enumerate(movement_array):
            if movement[0] == current_position[1]:
                return index

        return -1

    def sort_movements(self, movement_array):
        different_movements = []

        current_x = ord(self.position[0])
        current_y = int(self.position[1])

        left_front = []
        right_front = []

        if (self.player == 1 and self.can_eat) or (self.is_king and self.can_eat):
            left_front = [self.position, [str(chr(current_x - 1)), str(current_y + 1)]]
            right_front = [self.position, [str(chr(current_x + 1)), str(current_y + 1)]]

            try:
                movement_array.remove(left_front)
            except ValueError:
                pass

            try:
                movement_array.remove(right_front)
            except ValueError:
                pass

        if (self.player == 2 and self.can_eat) or (self.is_king and self.can_eat):
            left_front = [self.position, [str(chr(current_x - 1)), str(current_y - 1)]]
            right_front = [self.position, [str(chr(current_x + 1)), str(current_y - 1)]]

            try:
                movement_array.remove(left_front)
            except ValueError:
                pass

            try:
                movement_array.remove(right_front)
            except ValueError:
                pass

        if not self.can_eat:
            if self.player == 1 or self.is_king:
                left_front_search = [str(chr(current_x - 1)), str(current_y + 1)]
                right_front_search = [str(chr(current_x + 1)), str(current_y + 1)]

                if self.checkerboard.search_by_position(left_front_search, self.player) is not None:
                    try:
                        movement_array.remove(left_front)
                    except ValueError:
                        pass

                if self.checkerboard.search_by_position(right_front_search, self.player) is not None:
                    try:
                        movement_array.remove(right_front)
                    except ValueError:
                        pass

            if self.player == 2 or self.is_king:
                left_front_search = [str(chr(current_x - 1)), str(current_y - 1)]
                right_front_search = [str(chr(current_x + 1)), str(current_y - 1)]

                if self.checkerboard.search_by_position(left_front_search, self.player) is not None:
                    try:
                        movement_array.remove(left_front)
                    except ValueError:
                        pass

                if self.checkerboard.search_by_position(right_front_search, self.player) is not None:
                    try:
                        movement_array.remove(right_front)
                    except ValueError:
                        pass

        for movement in movement_array:
            if movement[0] == self.position:
                different_movements.append([movement])

        for movement in different_movements:
            index = self.has_next_movement(movement_array, movement[len(movement) - 1])
            while index != -1:
                movement.append(movement_array[index])
                index = self.has_next_movement(movement_array, movement[len(movement) - 1])
                if index != -1 and movement_array[index] in movement:
                    index = -1

        if self.can_eat:

            for movement in different_movements:
                individual_movement = 1
                while individual_movement < len(movement):
                    current_position = 2
                    while current_position < len(movement_array):

                        if movement_array[current_position] != movement[individual_movement] \
                                and movement[individual_movement][0] == movement_array[current_position][0] \
                                and movement_array[current_position] not in movement:
                            movement.append(movement_array[current_position])
                            index = self.has_next_movement(movement_array, movement[len(movement) - 1])
                            while index != -1:
                                movement.append(movement_array[index])
                                index = self.has_next_movement(movement_array, movement[len(movement) - 1])
                                if index != -1 and movement_array[index] in movement:
                                    index = -1

                        current_position += 1

                    individual_movement += 1

        return different_movements

    def display_movements(self, sorted_movements):
        for different_movement in sorted_movements:
            for individual_movement in different_movement:
                self.checkerboard.show_movement(individual_movement[1], self.id, "green")


class CheckerBoard:
    position_table_x = {"a": 100, "b": 200, "c": 300, "d": 400, "e": 500, "f": 600, "g": 700, "h": 800, "i": -10,
                        "j": -20,
                        "`": -30, "_": -40}

    position_table_y = {"1": 100, "2": 200, "3": 300, "4": 400, "5": 500, "6": 600, "7": 700, "8": 800, "9": -10,
                        "10": -20,
                        "0": -30, "-1": -40}

    def __init__(self, movement_time):
        self.mouse_position = None
        self.selected_directions = []
        self.process_mouse_id = None
        self.direction_index = 0
        self.final_path = []
        self.is_trapped = False
        self.none_left = False
        self.current_player = 1
        self.phase = "selection"
        self.checker_selected = None
        self.click_safe = True
        self.no_turns_player_1 = 0
        self.no_turns_player_2 = 0
        self.all_checkers = None
        self.player_one_ai = None
        self.player_two_ai = None
        self.movement_time = movement_time

        self.window = Tk()
        self.window.title("Checkers")

        self.canvas_width = 800
        self.canvas_height = 800

        self.canvas = Canvas(self.window, width=self.canvas_width, height=self.canvas_height, bg="black")
        self.canvas.pack()

    def init_one(self):
        vertical_spacings = int(round(self.canvas_width / 100, 0))
        horizontal_spacings = int(round(self.canvas_height / 100, 0))

        for x in range(0, vertical_spacings):
            self.canvas.create_line(x * 100, 0, x * 100, self.canvas_height, fill="white")

        for y in range(0, horizontal_spacings):
            self.canvas.create_line(0, y * 100, self.canvas_width, y * 100, fill="white")

        for x in range(100, self.canvas_width + 1, 100):
            color_start = "white"
            column = x / 100
            if column % 2 == 0:
                color_start = "black"

            for y in range(100, self.canvas_height + 1, 100):
                row = y / 100
                if row % 2 == 0:
                    if color_start == "black":
                        color = "white"
                    else:
                        color = "black"

                else:
                    color = color_start

                self.canvas.create_rectangle(x - 100, y - 100, x, y, fill=color)

        x_start = ord("b")
        y_start = 1

        player_one_checkers = []

        for current_checker in range(1, 13):
            position = [str(chr(x_start)), str(y_start)]
            c = Checker(position, "player1_c" + str(current_checker), "red", 1, self)
            player_one_checkers.append(c)

            if current_checker == 4:
                x_start = ord("a")
                y_start = 2

            elif current_checker == 8:
                x_start = ord("b")
                y_start = 3

            else:
                x_start += 2

        x_start = ord("a")
        y_start = 8
        player_two_checkers = []

        for current_checker in range(1, 13):
            position = [str(chr(x_start)), str(y_start)]
            c = Checker(position, "player2_c" + str(current_checker), "blue", 2, self)
            player_two_checkers.append(c)

            if current_checker == 4:
                x_start = ord("b")
                y_start = 7

            elif current_checker == 8:
                x_start = ord("a")
                y_start = 6

            else:
                x_start += 2

        self.all_checkers = [player_one_checkers, player_two_checkers]

    def bind_mouse(self):
        self.process_mouse_id = self.canvas.bind("<Button-1>", self.process_mouse_position)

    def search_by_position(self, position, player):
        """Checkers IDs are labelled from row 1-3 for player one and row 8-5 for player 2."""
        if player == 1:
            for checker in self.all_checkers[0]:
                if checker.get_position() == position:
                    return checker

        else:
            for checker in self.all_checkers[1]:
                if checker.get_position() == position:
                    return checker

        return None

    def get_neural_input(self):

        neural_input = []

        for y in range(1, 9):
            for x in range(ord("a"), ord("i")):
                current_position = [str(chr(x)), str(y)]
                checker = self.search_by_position(current_position, 1)
                if checker is None:
                    neural_input.append(0.0)
                else:
                    if checker.is_king:
                        neural_input.append(1.0)

                    else:
                        neural_input.append(0.5)

        for y in range(1, 9):
            for x in range(ord("a"), ord("i")):
                current_position = [str(chr(x)), str(y)]
                checker = self.search_by_position(current_position, 2)
                if checker is None:
                    neural_input.append(0.0)
                else:
                    if checker.is_king:
                        neural_input.append(1.0)

                    else:
                        neural_input.append(0.5)

        return neural_input

    def get_adaptive_input(self):
        neural_input = []

        for y in range(1, 9):
            for x in range(ord("a"), ord("i")):
                current_position = [str(chr(x)), str(y)]
                checker = self.search_by_position(current_position, self.current_player)
                if checker is None:
                    neural_input.append(0.0)
                else:
                    if checker.is_king:
                        neural_input.append(1.0)

                    else:
                        neural_input.append(0.5)

        for y in range(1, 9):
            for x in range(ord("a"), ord("i")):
                current_position = [str(chr(x)), str(y)]
                checker = self.search_by_position(current_position, self.switch_player(self.current_player))
                if checker is None:
                    neural_input.append(0.0)
                else:
                    if checker.is_king:
                        neural_input.append(1.0)

                    else:
                        neural_input.append(0.5)

        return neural_input

    def show_movement(self, position, tag, color):
        new_tag = tag + "p"
        x_position = self.position_table_x[position[0]]
        y_position = self.position_table_y[position[1]]
        self.canvas.create_rectangle(x_position - 100, y_position - 100, x_position, y_position, outline=color,
                                     tag=new_tag, width=4)

    def convert_mouse_position(self, coordinates):
        x = coordinates[0]
        y = coordinates[1]

        x_traverse = ord("a")
        while self.position_table_x[str(chr(x_traverse))] < x:
            x_traverse += 1

        y_traverse = 1
        while self.position_table_y[str(y_traverse)] < y:
            y_traverse += 1

        new_position = [str(chr(x_traverse)), str(y_traverse)]

        return new_position

    @staticmethod
    def switch_player(p):
        if p == 1:
            return 2
        return 1

    def check_if_trapped(self):
        player_checkers = self.all_checkers[self.current_player - 1]
        if len(player_checkers) == 0:
            return False

        for checker in player_checkers:
            if checker.get_can_move():
                return False

        return True

    def check_can_eat(self):
        player_checkers = self.all_checkers[self.current_player - 1]
        for checker in player_checkers:
            if checker.get_can_eat():
                return True

        return False

    def is_valid_click(self, valid_positions):
        for valid_position in valid_positions:
            if self.mouse_position == valid_position:
                return True

        return False

    def get_checker_index(self, player_number, checker_id):
        player_checkers = self.all_checkers[player_number - 1]
        for index, checker in enumerate(player_checkers):
            if checker.get_id() == checker_id:
                return index

        return -1

    def eat_checker(self, position, player_belonged):
        to_be_eaten = self.search_by_position(position, player_belonged)
        index = -1
        checker_id = None

        if to_be_eaten is not None:
            checker_id = to_be_eaten.get_id()
            index = self.get_checker_index(player_belonged, checker_id)

        if index != -1:
            self.canvas.delete(checker_id)
            del self.all_checkers[player_belonged - 1][index]

    def get_checkers_can_eat(self):
        checkers = []
        player_checkers = self.all_checkers[self.current_player - 1]
        for checker in player_checkers:
            if checker.get_can_eat():
                checkers.append(checker.get_position())

        return checkers

    def get_checkers_can_move(self):
        checkers = []
        player_checkers = self.all_checkers[self.current_player - 1]
        for checker in player_checkers:
            if checker.get_can_move():
                checkers.append(checker.get_position())

        return checkers

    def get_valid_positions(self, can_eat, movement_array):
        valid_positions = []
        if self.phase == "selection":
            if can_eat:
                valid_positions = self.get_checkers_can_eat()
                return valid_positions

            valid_positions = self.get_checkers_can_move()

        if self.phase == "checker_selected":
            for direction in movement_array:
                valid_positions.append(direction[0][1])

        if self.phase == "select_direction":
            for position in movement_array[self.direction_index][1]:
                valid_positions.append(position[1])

        return valid_positions

    def get_direction(self, movement_array):
        for direction in movement_array:
            if direction[0][1] == self.mouse_position:
                return direction

        return []

    @staticmethod
    def position_to_be_eaten(original_position, destination):
        original_x = ord(original_position[0])
        original_y = int(original_position[1])

        destination_x = ord(destination[0])
        destination_y = int(destination[1])

        if destination_x < original_x:
            if destination_y < original_y:
                return [str(chr(original_x - 1)), str(original_y - 1)]

            return [str(chr(original_x - 1)), str(original_y + 1)]

        if destination_x > original_x:
            if destination_y > original_y:
                return [str(chr(original_x + 1)), str(original_y + 1)]

            return [str(chr(original_x + 1)), str(original_y - 1)]

    @staticmethod
    def get_multi_directions(selected_direction):
        multi_direction_points = []
        compared_indices = []

        for index in range(1, len(selected_direction)):
            found_directions = False
            directions = []

            if index not in compared_indices:
                for to_compare in range(index + 1, len(selected_direction)):
                    if selected_direction[index][0] == selected_direction[to_compare][0]:
                        compared_indices.append(to_compare)
                        if not found_directions:
                            directions = [selected_direction[index], selected_direction[to_compare]]
                        else:
                            directions.append(selected_direction[to_compare])

                        found_directions = True

                if found_directions:
                    multi_direction_point = [selected_direction[index][0], directions]
                    multi_direction_points.append(multi_direction_point)

        return multi_direction_points

    def is_multi_directional(self, position, multi_points):
        for i in range(self.direction_index + 1, len(multi_points)):
            if position == multi_points[i][0]:
                return i

        return -1

    def return_position(self, event):
        event_position = [event.x, event.y]
        self.selected_directions = self.convert_mouse_position(event_position)

    def set_player_one_ai(self, mind):
        self.player_one_ai = mind

    def set_player_two_ai(self, mind):
        self.player_two_ai = mind

    def start_game(self):
        if self.player_one_ai is None and self.player_two_ai is None:
            self.bind_mouse()

        if self.player_one_ai is not None and self.player_two_ai is None:
            self.player_one_ai.make_move()
            self.bind_mouse()

        if self.player_one_ai is None and self.player_two_ai is not None:
            self.bind_mouse()

        if self.player_one_ai is not None and self.player_two_ai is not None:

            while not self.check_if_trapped() and len(self.all_checkers[self.current_player - 1]) > 0:

                if self.current_player == 1:
                    self.player_one_ai.make_move()

                else:
                    self.player_two_ai.make_move()

                for c in self.all_checkers[self.current_player - 1]:
                    c.movable()

            if self.current_player == 1:
                self.player_two_ai.is_winner = True
                print("Player two Won")

            if self.current_player == 2:
                self.player_one_ai.is_winner = True
                print("Player one Won")

            fitness_one = 0
            fitness_two = 0

            if self.player_one_ai.is_winner:
                fitness_one += 50

            if self.player_two_ai.is_winner:
                fitness_two += 50

            print("Player One Stats")
            stats = self.player_one_ai.get_stats()
            print("Number of Turns past : ", stats[0], "Number of Checkers left :", stats[1])
            print("Number of Checkers Eaten : ", stats[2], "Number of Kings : ", stats[3])
            print("Eating Ratio : ", (1 / stats[0]) * stats[2])
            if self.check_if_trapped() and self.current_player == 2:
                print("Player won by Trapped")
                fitness_one += 15

            if 30 >= stats[0] > 20:
                fitness_one += 10

            if 20 >= stats[0] > 15:
                fitness_one += 15

            if 15 >= stats[0] > 10:
                fitness_one += 20

            if stats[0] <= 10:
                fitness_one += 30

            fitness_one += (stats[1] * 2)

            fitness_one += ((1 / stats[0]) * stats[2]) * 100

            fitness_one += (stats[3] * 10)

            print("Player Two Stats")
            stats = self.player_two_ai.get_stats()
            print("Number of Turns past : ", stats[0], "Number of Checkers left :", stats[1])
            print("Number of Checkers Eaten : ", stats[2], "Number of Kings : ", stats[3])
            print("Eating Ratio : ", (1 / stats[0]) * stats[2])
            if self.check_if_trapped() and self.current_player == 1:
                print("Player won by Trapped")
                fitness_two += 15

            if 30 >= stats[0] > 20:
                fitness_two += 10

            if 20 >= stats[0] > 15:
                fitness_two += 15

            if 15 >= stats[0] > 10:
                fitness_two += 20

            if stats[0] <= 10:
                fitness_two += 30

            fitness_two += (stats[1] * 2)

            fitness_two += ((1 / stats[0]) * stats[2]) * 100

            fitness_two += (stats[3] * 10)

            return [fitness_one, fitness_two]

    def process_mouse_position(self, event):

        if not self.click_safe:
            return

        if self.current_player == 1 and self.player_one_ai is not None and not self.check_if_trapped() \
                and len(self.all_checkers[self.current_player - 1]) > 0:
            self.player_one_ai.make_move()
            return

        if self.current_player == 2 and self.player_two_ai is not None and not self.check_if_trapped() \
                and len(self.all_checkers[self.current_player - 1]) > 0:
            self.player_two_ai.make_move()
            return

        self.mouse_position = [event.x, event.y]
        self.mouse_position = self.convert_mouse_position(self.mouse_position)
        print("Position Selected : ", self.mouse_position)

        if self.phase == "select_direction":
            selected_id = self.checker_selected.get_id()
            multi_points = self.get_multi_directions(self.selected_directions)

            if not self.final_path:
                self.final_path.append(self.selected_directions[0])

            valid_positions = self.get_valid_positions(None, multi_points)

            if self.is_valid_click(valid_positions):

                movement = self.checker_selected.has_next_movement(self.selected_directions,
                                                                   self.final_path[len(self.final_path) - 1])
                while movement != -1:

                    if self.selected_directions[movement][0] == multi_points[self.direction_index][0]:
                        self.final_path.append([self.final_path[len(self.final_path) - 1][1], self.mouse_position])

                        movement = self.checker_selected.has_next_movement(self.selected_directions,
                                                                           self.final_path[len(self.final_path) - 1])

                        if movement != -1 and self.selected_directions[movement] in self.final_path:
                            movement = -1

                    multi_index = -1
                    if movement != -1:
                        multi_index = self.is_multi_directional(self.selected_directions[movement][0], multi_points)
                    if multi_index != -1:
                        for alternative_direction in multi_points[multi_index][1]:
                            self.show_movement(alternative_direction[1], selected_id, "brown")

                        self.direction_index = multi_index
                        return

                    if movement != -1:
                        self.final_path.append(self.selected_directions[movement])

                        movement = self.checker_selected.has_next_movement(self.selected_directions,
                                                                           self.final_path[len(self.final_path) - 1])

                        if movement != -1 and self.selected_directions[movement] in self.final_path:
                            movement = -1

                self.canvas.delete(selected_id + "p")
                for movement in self.final_path:
                    destination = movement[1]

                    checker_to_be_eaten = self.position_to_be_eaten(self.checker_selected.get_position(),
                                                                    destination)
                    print("Checker ", checker_to_be_eaten, "Eaten From ", self.checker_selected.get_position())

                    self.checker_selected.move_to(destination)
                    self.eat_checker(checker_to_be_eaten, self.switch_player(self.current_player))

                self.current_player = self.switch_player(self.current_player)

                if self.current_player == 1 and self.player_one_ai is not None and not self.check_if_trapped() \
                        and len(self.all_checkers[self.current_player - 1]) > 0:
                    self.player_one_ai.make_move()

                if self.current_player == 2 and self.player_two_ai is not None and not self.check_if_trapped() \
                        and len(self.all_checkers[self.current_player - 1]) > 0:
                    self.player_two_ai.make_move()

                self.phase = "selection"
                return

            else:
                self.final_path = []
                self.direction_index = 0
                self.canvas.delete(selected_id + "p")
                self.phase = "selection"

        if self.phase == "checker_selected":
            selected_id = self.checker_selected.get_id()
            movement_array = self.checker_selected.get_movements()
            movement_array = self.checker_selected.sort_movements(movement_array)
            valid_positions = self.get_valid_positions(None, movement_array)

            if self.is_valid_click(valid_positions):
                can_eat = self.checker_selected.get_can_eat()
                if not can_eat:
                    self.canvas.delete(selected_id + "p")
                    self.checker_selected.move_to(self.mouse_position)
                    self.current_player = self.switch_player(self.current_player)

                    if self.current_player == 1 and self.player_one_ai is not None and not self.check_if_trapped() \
                            and len(self.all_checkers[self.current_player - 1]) > 0:
                        self.player_one_ai.make_move()

                    if self.current_player == 2 and self.player_two_ai is not None and not self.check_if_trapped() \
                            and len(self.all_checkers[self.current_player - 1]) > 0:
                        self.player_two_ai.make_move()

                    self.phase = "selection"
                    return

                else:
                    selected_direction = self.get_direction(movement_array)
                    multi_points = self.get_multi_directions(selected_direction)

                    if multi_points:
                        for alternative_direction in multi_points[0][1]:
                            self.show_movement(alternative_direction[1], selected_id, "orange")

                        self.phase = "select_direction"
                        self.selected_directions = selected_direction
                        return

                    self.canvas.delete(selected_id + "p")

                    for movement in selected_direction:
                        destination = movement[1]

                        checker_to_be_eaten = self.position_to_be_eaten(self.checker_selected.get_position(),
                                                                        destination)
                        print("Checker ", checker_to_be_eaten, "Eaten From ", self.checker_selected.get_position())

                        self.checker_selected.move_to(destination)
                        self.eat_checker(checker_to_be_eaten, self.switch_player(self.current_player))

                    self.current_player = self.switch_player(self.current_player)

                    if self.current_player == 1 and self.player_one_ai is not None and not self.check_if_trapped() \
                            and len(self.all_checkers[self.current_player - 1]) > 0:
                        self.player_one_ai.make_move()

                    if self.current_player == 2 and self.player_two_ai is not None and not self.check_if_trapped() \
                            and len(self.all_checkers[self.current_player - 1]) > 0:
                        self.player_two_ai.make_move()

                    self.phase = "selection"
                    return

            else:
                self.canvas.delete(selected_id + "p")
                self.phase = "selection"

        if self.phase == "selection":

            for c in self.all_checkers[self.current_player - 1]:
                c.movable()

            checkers_left = len(self.all_checkers[self.current_player - 1])

            if not self.check_if_trapped() and checkers_left > 0:
                print("Player ", self.current_player, " Status : ", "Not Trapped", "Checkers left : ", checkers_left)
                can_eat = self.check_can_eat()
                if can_eat:
                    valid_positions = self.get_valid_positions(can_eat, None)

                    for pos in valid_positions:
                        must_eat_checker = self.search_by_position(pos, self.current_player)
                        movement_array = must_eat_checker.get_movements()
                        movement_array = must_eat_checker.sort_movements(movement_array)
                        must_eat_checker.display_movements(movement_array)

                    if self.is_valid_click(valid_positions):
                        self.checker_selected = self.search_by_position(self.mouse_position, self.current_player)
                        for pos in valid_positions:
                            if pos != self.mouse_position:
                                unselected = self.search_by_position(pos, self.current_player)
                                unselected_movement_id = unselected.get_id()
                                self.canvas.delete(unselected_movement_id + "p")

                        self.phase = "checker_selected"

                        selected_id = self.checker_selected.get_id()
                        movement_array = self.checker_selected.get_movements()
                        movement_array = self.checker_selected.sort_movements(movement_array)
                        valid_positions = self.get_valid_positions(None, movement_array)

                        for pos in valid_positions:
                            self.show_movement(pos, selected_id, "yellow")

                else:
                    valid_positions = self.get_valid_positions(can_eat, None)
                    if self.is_valid_click(valid_positions):
                        self.checker_selected = self.search_by_position(self.mouse_position, self.current_player)
                        movement_array = self.checker_selected.get_movements()
                        movement_array = self.checker_selected.sort_movements(movement_array)
                        self.checker_selected.display_movements(movement_array)

                        self.phase = "checker_selected"

            else:
                print("Player ", self.current_player, "Lost\n", "PLAYER ", self.switch_player(self.current_player),
                      "WON!!")
                self.window.destroy()


class Body:
    def __init__(self, mind):
        self.mind = mind
        self.selected_checker = None

    def move_checker_at(self, position_of_checker, destination):
        checker = self.mind.board.search_by_position(position_of_checker, self.mind.player)

        if checker is not None:
            checker.move_to(destination)
            return True

        return False

    def move_selected_checker(self, destination):
        if self.selected_checker is not None:
            self.selected_checker.move_to(destination)
            return True

        return False

    def select_checker(self, position_of_checker):
        self.selected_checker = self.mind.board.search_by_position(position_of_checker, self.mind.player)

        if self.selected_checker is not None:
            return True

        return False

    def eat_opponent_checker(self, path):
        self.select_checker(path[0][0])

        if self.selected_checker.is_king:
            self.mind.was_king = True

        for movement in path:
            destination = movement[1]

            checker_to_be_eaten = self.mind.board.position_to_be_eaten(self.selected_checker.get_position(),
                                                                       destination)
            # print("Checker ", checker_to_be_eaten, "Eaten From ", self.selected_checker.get_position())

            self.selected_checker.move_to(destination)
            self.mind.board.eat_checker(checker_to_be_eaten, self.mind.board.switch_player(self.mind.player))

        if self.selected_checker.is_king and not self.mind.was_king:
            self.mind.number_of_kings += 1

        self.selected_checker = None


class Mind:
    def update_brain(self, updated_brain):
        for index in range(len(updated_brain)):
            if index < 64:
                self.base_brain[index % 64]["movement_rank"] = updated_brain[index]

            else:
                self.base_brain[index % 64]["checker_rank"] = updated_brain[index]

    def adapt_situation(self, adaptations):
        for index in range(len(adaptations)):
            if index < 64:
                self.brain[index % 64]["movement_rank"] = self.base_brain[index % 64]["movement_rank"] + adaptations[
                    index]
                if self.brain[index % 64]["movement_rank"] < 0:
                    self.brain[index % 64]["movement_rank"] = 0

            else:
                self.brain[index % 64]["checker_rank"] = self.base_brain[index % 64]["checker_rank"] + adaptations[
                    index]
                if self.brain[index % 64]["checker_rank"] < 0:
                    self.brain[index % 64]["checker_rank"] = 0

    def __init__(self, checkerboard, player, brain):
        self.player = player
        self.checker_side = checkerboard.all_checkers[player - 1]
        self.board = checkerboard
        self.number_checkers_left = len(self.checker_side)
        self.number_of_turns_passed = 0
        self.number_of_kings = 0
        self.checker_eaten = 0
        self.was_king = False
        self.body = Body(self)
        self.base_brain = []
        self.brain = []
        self.genome = None
        self.adaptive_brain = None

        self.is_winner = False

        if brain is not None:
            for i in range(ord("a"), ord("i")):
                for j in range(1, 9):
                    self.base_brain.append(
                        {"position": [str(chr(i)), str(j)], "movement_rank": None, "checker_rank": None})

            self.update_brain(brain)
            self.brain = copy.deepcopy(self.base_brain)

    def set_adaptive_brain(self, genome, config):
        self.genome = genome
        adaptive_brain = neat.nn.FeedForwardNetwork.create(genome, config)
        self.adaptive_brain = adaptive_brain

    def set_base_brain(self, base_brain):
        self.base_brain = base_brain
        self.brain = copy.deepcopy(self.base_brain)

    def set_adaptive_and_base(self, genome, config, base_brain):
        self.genome = genome
        adaptive_brain = neat.nn.FeedForwardNetwork.create(genome, config)
        self.adaptive_brain = adaptive_brain
        self.base_brain = base_brain
        self.brain = copy.deepcopy(self.base_brain)

    def save_genome(self):
        with open("adBrain.dat", "wb") as c:
            pickle.dump(self.genome, c)

    def load_genome(self, config):
        with open("adBrain.dat", "rb") as c:
            self.genome = pickle.load(c)
            self.base_brain = get_base_brain()
            self.adaptive_brain = neat.nn.FeedForwardNetwork.create(self.genome, config)
            self.brain = copy.deepcopy(self.base_brain)

    def save_base_brain(self):
        with open("bBrain.dat", "wb") as c:
            pickle.dump(self.base_brain, c)

    def get_movable_checkers(self):
        movable_checkers = []
        for checker in self.checker_side:
            if checker.get_can_move():
                movable_checkers.append(checker)

        return movable_checkers

    def get_checkers_can_eat(self):
        can_eat_checkers = []
        for checker in self.checker_side:
            if checker.get_can_eat():
                can_eat_checkers.append(checker)

        return can_eat_checkers

    @staticmethod
    def search_checkers(position, checkers):
        for checker in checkers:
            if checker.get_position() == position:
                return checker

        return None

    @staticmethod
    def get_all_movable_positions(movable):
        all_movements = []
        for checker in movable:
            movement_array = checker.get_movements()
            movement_array = checker.sort_movements(movement_array)
            all_movements.append(movement_array)

        return all_movements

    @staticmethod
    def get_single_movable_position(checker):
        movement_array = checker.get_movements()
        movement_array = checker.sort_movements(movement_array)
        movable_positions = []
        for movement in movement_array:
            for direction in movement:
                movable_positions.append(direction[1])

        return movable_positions

    @staticmethod
    def sort_all_movements(all_movements):
        sorted_movements = []
        for checker in all_movements:
            for movement in checker:
                for destination in movement:
                    if destination[1] not in sorted_movements:
                        sorted_movements.append(destination[1])

        return sorted_movements

    @staticmethod
    def get_sources(all_movements, destination):
        sources = []
        for checker in all_movements:
            for movement in checker:
                for source in movement:
                    if source[1] == destination:
                        sources.append(movement[0][0])

        return sources

    @staticmethod
    def is_multi_directional(position, multi_directional):
        if multi_directional:
            for index, multi_position in enumerate(multi_directional):
                if position[1] == multi_position[0]:
                    return index

        return -1

    def get_multi_destinations(self, movement, multi_directional, destinations, path, count):
        index = Checker.has_next_movement(movement, path[len(path) - 1])
        if index == -1 or index == 0 or movement[index] in path:
            p = copy.deepcopy(path)
            # Since python runs asynchronously. values in path will be updated before appended.
            destinations.append([path[len(path) - 1][1], count, p])
            # Copy values in path before new values appended
            del path[len(path) - 1]
            return

        multi_index = self.is_multi_directional(path[len(path) - 1], multi_directional)
        if multi_index != -1:
            for direction in multi_directional[multi_index][1]:
                path.append(direction)
                self.get_multi_destinations(movement, multi_directional, destinations, path, count + 1)
            return

        path.append(movement[index])
        self.get_multi_destinations(movement, multi_directional, destinations, path, count + 1)

    def sort_eating_movements(self, all_movements):
        destinations = []
        for checker in all_movements:
            for movement in checker:
                path = [movement[0]]
                multi_directional = self.board.get_multi_directions(movement)
                self.get_multi_destinations(movement, multi_directional, destinations, path, 1)

        return destinations

    def get_ranks(self, checkers):
        ranks = []
        for checker in checkers:
            for rank in self.brain:
                if checker.get_position() == rank["position"]:
                    ranks.append(rank)

        return ranks

    @staticmethod
    def roulette_wheel(cdf):
        selector = numpy.random.uniform(0, 100)
        for index, value in enumerate(cdf):
            if selector <= value:
                return index

    def select_checker_or_movement(self, movable_checkers, movements, eat_movements):
        if movable_checkers:

            if len(movable_checkers) == 1:
                return movable_checkers[0]

            ranks = self.get_ranks(movable_checkers)

            total_checker_rank = 0
            rank_cdf = []

            for rank in ranks:
                total_checker_rank += rank["checker_rank"]

            if total_checker_rank == 0:
                return movable_checkers[0]

            for rank in ranks:
                rank_cdf.append((rank["checker_rank"] / total_checker_rank) * 100)

            rank_cdf = numpy.cumsum(rank_cdf)
            index = self.roulette_wheel(rank_cdf)
            return movable_checkers[index]

        if movements:

            if len(movements) == 1:
                return movements[0]

            ranks = []
            for movement in movements:
                for rank in self.brain:
                    if movement == rank["position"]:
                        ranks.append(rank)

            total_checker_rank = 0
            rank_cdf = []

            for rank in ranks:
                total_checker_rank += rank["checker_rank"]

            if total_checker_rank == 0:
                return movements[0]

            for rank in ranks:
                rank_cdf.append((rank["checker_rank"] / total_checker_rank) * 100)

            rank_cdf = numpy.cumsum(rank_cdf)
            index = self.roulette_wheel(rank_cdf)
            selected_position = ranks[index]["position"]

            return selected_position

        if eat_movements:
            if len(eat_movements) == 1:
                return eat_movements[0][2]

            ranks = []
            for movement in eat_movements:
                for rank in self.brain:
                    if movement[0] == rank["position"]:
                        ranks.append(rank)

            total_checker_rank = 0
            rank_cdf = []
            adjusted_movement_ranks = []

            for i in range(len(ranks)):
                adjusted_movement_ranks.append(ranks[i]["movement_rank"] + (0.25 * eat_movements[i][1]))

            for rank in adjusted_movement_ranks:
                total_checker_rank += rank

            if total_checker_rank == 0:
                return eat_movements[0][2]

            for rank in adjusted_movement_ranks:
                rank_cdf.append((rank / total_checker_rank) * 100)

            rank_cdf = numpy.cumsum(rank_cdf)
            index = self.roulette_wheel(rank_cdf)
            return eat_movements[index][2]

    def print_brain(self):
        for neuron in self.brain:
            print(neuron)

    def make_move(self):
        for c in self.checker_side:
            c.movable()

        can_eat = self.get_checkers_can_eat()

        if self.number_of_turns_passed < 1:

            if len(can_eat) > 0:
                selected_checker = self.select_checker_or_movement(can_eat, None, None)
                movement_array = selected_checker.get_movements()
                movement_array = selected_checker.sort_movements(movement_array)
                sort = self.sort_eating_movements([movement_array])
                if self.adaptive_brain is not None:
                    inputs = self.board.get_adaptive_input()
                    adaptations = self.adaptive_brain.activate(inputs)
                    self.adapt_situation(adaptations)
                path = self.select_checker_or_movement(None, None, sort)
                self.body.eat_opponent_checker(path)
                self.checker_eaten += len(path)

            else:
                movable_checkers = self.get_movable_checkers()
                if self.adaptive_brain is not None:
                    inputs = self.board.get_adaptive_input()
                    adaptations = self.adaptive_brain.activate(inputs)
                    self.adapt_situation(adaptations)
                selected_checker = self.select_checker_or_movement(movable_checkers, None, None)
                if selected_checker.is_king:
                    self.was_king = True

                movements = self.get_single_movable_position(selected_checker)
                selected_destination = self.select_checker_or_movement(None, movements, None)
                selected_checker.move_to(selected_destination)
                if selected_checker.is_king and not self.was_king:
                    self.number_of_kings += 1

        else:
            best_predicted_move = predictor.get_prediction(self.board.get_neural_input(), self.player, self.base_brain,
                                                           self.adaptive_brain)

            if best_predicted_move["can_eat"]:
                self.body.eat_opponent_checker(best_predicted_move["move"])
                self.checker_eaten += len(best_predicted_move["move"])

            else:
                selected_checker = self.board.search_by_position(best_predicted_move["move"][0], self.player)
                selected_checker.move_to(best_predicted_move["move"][1])

        self.board.current_player = self.board.switch_player(self.player)
        self.number_checkers_left = len(self.checker_side)
        self.number_of_turns_passed += 1
        self.was_king = False

    def get_stats(self):
        return [self.number_of_turns_passed, self.number_checkers_left, self.checker_eaten, self.number_of_kings]


def run_neural_tournament(selected_genomes, config, base_brain, checkerboard):
    for genome in selected_genomes:
        genome.fitness = 50.0

    checkerboard.init_one()
    player_one = Mind(checkerboard, 1, None)
    player_two = Mind(checkerboard, 2, None)
    player_one.set_adaptive_and_base(selected_genomes[0], config, base_brain)
    player_two.set_adaptive_and_base(selected_genomes[3], config, base_brain)

    checkerboard.set_player_one_ai(player_one)
    checkerboard.set_player_two_ai(player_two)
    print("Player : 0 VS Player : 3")
    fitness_values = checkerboard.start_game()
    checkerboard.canvas.delete("all")

    selected_genomes[0].fitness += fitness_values[0]
    selected_genomes[3].fitness += fitness_values[1]

    checkerboard.init_one()
    player_three = Mind(checkerboard, 1, None)
    player_four = Mind(checkerboard, 2, None)
    player_three.set_adaptive_and_base(selected_genomes[1], config, base_brain)
    player_four.set_adaptive_and_base(selected_genomes[4], config, base_brain)

    checkerboard.set_player_one_ai(player_three)
    checkerboard.set_player_two_ai(player_four)
    print("Player : 1 VS Player : 4")
    fitness_values = checkerboard.start_game()
    checkerboard.canvas.delete("all")

    selected_genomes[1].fitness += fitness_values[0]
    selected_genomes[4].fitness += fitness_values[1]

    checkerboard.init_one()
    player_five = Mind(checkerboard, 1, None)
    player_six = Mind(checkerboard, 2, None)
    player_five.set_adaptive_and_base(selected_genomes[2], config, base_brain)
    player_six.set_adaptive_and_base(selected_genomes[5], config, base_brain)

    checkerboard.set_player_one_ai(player_five)
    checkerboard.set_player_two_ai(player_six)
    print("Player : 2 VS Player : 5")
    fitness_values = checkerboard.start_game()
    checkerboard.canvas.delete("all")

    selected_genomes[2].fitness += fitness_values[0]
    selected_genomes[5].fitness += fitness_values[1]

    checkerboard.init_one()
    player_seven = Mind(checkerboard, 1, None)
    player_eight = Mind(checkerboard, 2, None)
    player_seven.set_adaptive_and_base(selected_genomes[6], config, base_brain)
    player_eight.set_adaptive_and_base(selected_genomes[7], config, base_brain)

    checkerboard.set_player_one_ai(player_seven)
    checkerboard.set_player_two_ai(player_eight)
    print("Player : 6 VS Player : 7")
    fitness_values = checkerboard.start_game()
    checkerboard.canvas.delete("all")

    selected_genomes[6].fitness += fitness_values[0]
    selected_genomes[7].fitness += fitness_values[1]

    players = [player_one, player_three, player_five, player_two, player_four, player_six, player_seven,
               player_eight]

    winners = []
    for i in range(8):
        if players[i].is_winner:
            winners.append(i)
    print("Winners : ", winners)
    checkerboard.init_one()
    player_one = Mind(checkerboard, 1, None)
    player_two = Mind(checkerboard, 2, None)
    player_one.set_adaptive_and_base(selected_genomes[winners[0]], config, base_brain)
    player_two.set_adaptive_and_base(selected_genomes[winners[1]], config, base_brain)

    checkerboard.set_player_one_ai(player_one)
    checkerboard.set_player_two_ai(player_two)
    print("Player : ", winners[0], " VS Player :", winners[1])
    fitness_values = checkerboard.start_game()
    checkerboard.canvas.delete("all")

    selected_genomes[winners[0]].fitness += fitness_values[0]
    selected_genomes[winners[1]].fitness += fitness_values[1]

    checkerboard.init_one()
    player_three = Mind(checkerboard, 1, None)
    player_four = Mind(checkerboard, 2, None)
    player_three.set_adaptive_and_base(selected_genomes[winners[2]], config, base_brain)
    player_four.set_adaptive_and_base(selected_genomes[winners[3]], config, base_brain)

    checkerboard.set_player_one_ai(player_three)
    checkerboard.set_player_two_ai(player_four)
    print("Player : ", winners[2], " VS Player :", winners[3])
    fitness_values = checkerboard.start_game()
    checkerboard.canvas.delete("all")

    selected_genomes[winners[2]].fitness += fitness_values[0]
    selected_genomes[winners[3]].fitness += fitness_values[1]

    players = [player_one, player_two, player_three, player_four]

    semi_winners = []
    for i in range(4):
        if players[i].is_winner:
            semi_winners.append(winners[i])
    print("Winners Semi Final : ", semi_winners)
    checkerboard.init_one()
    player_one = Mind(checkerboard, 1, None)
    player_two = Mind(checkerboard, 2, None)
    player_one.set_adaptive_and_base(selected_genomes[semi_winners[0]], config, base_brain)
    player_two.set_adaptive_and_base(selected_genomes[semi_winners[1]], config, base_brain)

    checkerboard.set_player_one_ai(player_one)
    checkerboard.set_player_two_ai(player_two)
    print("Player : ", semi_winners[0], " VS Player :", semi_winners[1])
    fitness_values = checkerboard.start_game()
    checkerboard.canvas.delete("all")

    selected_genomes[semi_winners[0]].fitness += fitness_values[0]
    selected_genomes[semi_winners[1]].fitness += fitness_values[1]

    if player_one.is_winner:
        print("Tournament Winner : ", semi_winners[0])
    else:
        print("Tournament Winner : ", semi_winners[1])


def run_neural_top_contender(stripped_genomes, config, base_brain, checkerboard, generation_number):
    match_number = 1
    number_matches_won = 0
    highest_number_won = 0
    current_contender = stripped_genomes[0]

    for opponent_selector in range(1, len(stripped_genomes)):
        current_opponent = stripped_genomes[opponent_selector]
        checkerboard.init_one()
        selected_side = numpy.random.uniform(0, 1)

        if selected_side <= 0.5:
            contender = Mind(checkerboard, 1, None)
            opponent = Mind(checkerboard, 2, None)
            contender.set_adaptive_and_base(current_contender, config, base_brain)
            opponent.set_adaptive_and_base(current_opponent, config, base_brain)
            checkerboard.set_player_one_ai(contender)
            checkerboard.set_player_two_ai(opponent)

        else:
            contender = Mind(checkerboard, 2, None)
            opponent = Mind(checkerboard, 1, None)
            contender.set_adaptive_and_base(current_contender, config, base_brain)
            opponent.set_adaptive_and_base(current_opponent, config, base_brain)
            checkerboard.set_player_one_ai(opponent)
            checkerboard.set_player_two_ai(contender)

        print("*****************************************************************************")
        print("Match number : ", match_number, "Generation : ", generation_number, "Highest Wins :", highest_number_won)
        print("Current Contender Already Racked : ", number_matches_won, " Wins")
        print("*****************************************************************************")

        fitness_values = checkerboard.start_game()
        checkerboard.canvas.delete("all")
        match_number += 1

        if selected_side <= 0.5:
            current_contender.fitness += fitness_values[0]
            current_opponent.fitness += fitness_values[1]

        else:
            current_opponent.fitness += fitness_values[0]
            current_contender.fitness += fitness_values[1]

        if opponent.is_winner:
            current_contender = current_opponent
            number_matches_won = 0

        else:
            number_matches_won += 1

        if number_matches_won > highest_number_won:
            highest_number_won = number_matches_won


def really_inefficient_tournament(stripped_genomes, config, base_brain, checkerboard, generation_number,
                                  number_of_matches):
    highest_number_won = 0

    for contender_selector in range(len(stripped_genomes)):
        current_contender = stripped_genomes[contender_selector]
        number_matches_won = 0
        previous_opponents = [contender_selector]

        for match_number in range(number_of_matches):
            opponent_selector = numpy.random.randint(len(stripped_genomes))
            while opponent_selector in previous_opponents:
                opponent_selector = numpy.random.randint(len(stripped_genomes))

            previous_opponents.append(opponent_selector)
            current_opponent = stripped_genomes[opponent_selector]

            checkerboard.init_one()
            selected_side = numpy.random.uniform(0, 1)

            if selected_side <= 0.5:
                contender = Mind(checkerboard, 1, None)
                opponent = Mind(checkerboard, 2, None)
                contender.set_adaptive_and_base(current_contender, config, base_brain)
                opponent.set_adaptive_and_base(current_opponent, config, base_brain)
                checkerboard.set_player_one_ai(contender)
                checkerboard.set_player_two_ai(opponent)

            else:
                contender = Mind(checkerboard, 2, None)
                opponent = Mind(checkerboard, 1, None)
                contender.set_adaptive_and_base(current_contender, config, base_brain)
                opponent.set_adaptive_and_base(current_opponent, config, base_brain)
                checkerboard.set_player_one_ai(opponent)
                checkerboard.set_player_two_ai(contender)

            print("*****************************************************************************")
            print("Match number : ", match_number, "Generation : ", generation_number, "Highest Wins :",
                  highest_number_won)

            if selected_side <= 0.5:
                print("Contender : ", contender_selector, " VS Opponent : ", opponent_selector)
            else:
                print("Opponent : ", opponent_selector, " VS Contender :", contender_selector)

            print("Current Contender ", contender_selector, " Already Racked : ", number_matches_won, " Wins")
            print("Current Contender ", contender_selector, " Fitness at : ", current_contender.fitness)
            print("*****************************************************************************")

            fitness_values = checkerboard.start_game()
            checkerboard.canvas.delete("all")

            if selected_side <= 0.5:
                current_contender.fitness += fitness_values[0]

            else:
                current_contender.fitness += fitness_values[1]

            if contender.is_winner:
                number_matches_won += 1

            if number_matches_won > highest_number_won:
                highest_number_won = number_matches_won


def kind_of_improved_tournament(stripped_genomes, config, base_brain, checkerboard, generation_number,
                                number_of_matches):
    highest_number_won = 0
    global highest_fitness

    for contender_selector in range(len(stripped_genomes)):
        current_contender = stripped_genomes[contender_selector]
        number_matches_won = 0
        previous_opponents = [contender_selector]

        for match_number in range(number_of_matches):
            opponent_selector = numpy.random.randint(len(stripped_genomes))
            while opponent_selector in previous_opponents:
                opponent_selector = numpy.random.randint(len(stripped_genomes))

            previous_opponents.append(opponent_selector)
            current_opponent = stripped_genomes[opponent_selector]

            checkerboard.init_one()
            selected_side = numpy.random.uniform(0, 1)

            if selected_side <= 0.5:
                contender = Mind(checkerboard, 1, None)
                opponent = Mind(checkerboard, 2, None)
                contender.set_adaptive_and_base(current_contender, config, base_brain)
                opponent.set_adaptive_and_base(current_opponent, config, base_brain)
                checkerboard.set_player_one_ai(contender)
                checkerboard.set_player_two_ai(opponent)

            else:
                contender = Mind(checkerboard, 2, None)
                opponent = Mind(checkerboard, 1, None)
                contender.set_adaptive_and_base(current_contender, config, base_brain)
                opponent.set_adaptive_and_base(current_opponent, config, base_brain)
                checkerboard.set_player_one_ai(opponent)
                checkerboard.set_player_two_ai(contender)

            print("*****************************************************************************")
            print("Match number : ", match_number, "Generation : ", generation_number, "Highest Wins :",
                  highest_number_won)
            print("Highest Fitness : ", highest_fitness)

            if selected_side <= 0.5:
                print("Contender : ", contender_selector, " VS Opponent : ", opponent_selector)
            else:
                print("Opponent : ", opponent_selector, " VS Contender :", contender_selector)

            print("Current Contender ", contender_selector, " Already Racked : ", number_matches_won, " Wins")
            print("Current Contender ", contender_selector, " Fitness at : ", current_contender.fitness)
            print("*****************************************************************************")

            fitness_values = checkerboard.start_game()
            checkerboard.canvas.delete("all")

            if selected_side <= 0.5:
                current_contender.fitness += fitness_values[0]

            else:
                current_contender.fitness += fitness_values[1]

            if current_contender.fitness > highest_fitness:
                highest_fitness = current_contender.fitness

            if contender.is_winner:
                number_matches_won += 1

            else:
                break

            if number_matches_won > highest_number_won:
                highest_number_won = number_matches_won

            if number_matches_won == number_of_matches:
                current_contender.fitness += 5000.0


def get_base_brain():
    with open("bBrain.dat", "rb") as c:
        base_brain = pickle.load(c)

    return base_brain


# Neat Implementation
def eval_genomes(genomes, config):
    global current_top_brain
    global generation_number
    global c_board
    prev_index = 0
    tournament_number = 1
    generation_number += 1

    for index in range(8, len(genomes) + 1, 8):
        selected = []
        selected_genome = []

        for selector in range(prev_index, index):
            selected.append(genomes[selector])
        for genome_id, genome in selected:
            selected_genome.append(genome)

        prev_index = index
        print("Genome Length : ", len(genomes))
        print("***********\nTOURNAMENT NUMBER ", tournament_number, "OF GENERATION ", generation_number)
        run_neural_tournament(selected_genome, config, current_top_brain, c_board)
        tournament_number += 1


def eval_genome_updated(genomes, config):
    global current_top_brain
    global generation_number
    global c_board
    generation_number += 1

    stripped_genomes = []
    for genome_id, genome in genomes:
        genome.fitness = 0.0
        stripped_genomes.append(genome)

    run_neural_top_contender(stripped_genomes, config, current_top_brain, c_board, generation_number)


def eval_genome_inefficient(genomes, config):
    global current_top_brain
    global generation_number
    global c_board
    generation_number += 1

    stripped_genomes = []
    for genome_id, genome in genomes:
        genome.fitness = 0.0
        stripped_genomes.append(genome)

    really_inefficient_tournament(stripped_genomes, config, current_top_brain, c_board, generation_number, 10)


def eval_genome_improved(genomes, config):
    global current_top_brain
    global generation_number
    global c_board
    generation_number += 1

    stripped_genomes = []
    for genome_id, genome in genomes:
        genome.fitness = 0.0
        stripped_genomes.append(genome)

    kind_of_improved_tournament(stripped_genomes, config, current_top_brain, c_board, generation_number, 10)


def train_adaptive_brain(config, save_to_file):
    global current_top_brain
    current_top_brain = get_base_brain()

    new_city = neat.Population(config)
    new_city.add_reporter(neat.StdOutReporter(False))

    winning_genome = new_city.run(eval_genome_improved)

    if save_to_file:
        c = CheckerBoard(0)
        c.init_one()
        top_mind = Mind(c, 1, None)
        top_mind.set_adaptive_and_base(winning_genome, config, current_top_brain)
        top_mind.save_genome()


def play_checkers(selected_player):
    checkerboard = CheckerBoard(0.01)
    checkerboard.init_one()

    if selected_player == 0:
        checkerboard.start_game()
        mainloop()

    elif selected_player == 2:
        player = Mind(checkerboard, 1, None)
        player.load_genome(config)
        checkerboard.set_player_one_ai(player)
        checkerboard.start_game()
        mainloop()

    else:
        player = Mind(checkerboard, 2, None)
        player.load_genome(config)
        checkerboard.set_player_two_ai(player)
        checkerboard.start_game()
        mainloop()


config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                     neat.DefaultStagnation, 'config-feedforward')

generation_number = -1
highest_fitness = 0
current_top_brain = None

# Uncomment to train neural network
#c_board = CheckerBoard(0)
#train_adaptive_brain(config, True)

# Uncomment to play checkers with final generation of AI(set parameter as 1 or 2) or to play against friend(set parameter as 0)
play_checkers(2)

