import copy
import numpy
import neat


class Checkerboard:
    def __init__(self, positions=None):
        self.checkerboard = []
        self.all_checkers = []
        self.direction_index = 0
        self.final_path = []
        self.is_trapped = False
        self.current_player = 1
        self.predictor_ai = None
        self.player_one_ai = None
        self.player_two_ai = None

        x_position = ord("a")
        y_position = 1

        for y_traverse in range(8):
            self.checkerboard.append([])
            for x_traverse in range(8):
                self.checkerboard[len(self.checkerboard) - 1].append(
                    {"position": [str(chr(x_position)), str(y_position)],
                     "checker": 0, "player": 0, "can_eat": False,
                     "can_move": False})
                x_position += 1

            x_position = ord("a")
            y_position += 1

        player_one_checkers = []
        player_two_checkers = []

        if positions is None:
            player_one_y = 1
            player_two_y = 8
            player_one_x = 2
            player_two_x = 7

            for i in range(12):
                self.checkerboard[player_one_y - 1][player_one_x - 1]["checker"] = 0.5
                self.checkerboard[player_one_y - 1][player_one_x - 1]["player"] = 1
                self.checkerboard[player_two_y - 1][player_two_x - 1]["checker"] = 0.5
                self.checkerboard[player_two_y - 1][player_two_x - 1]["player"] = 2
                player_one_checkers.append(self.checkerboard[player_one_y - 1][player_one_x - 1])
                player_two_checkers.append(self.checkerboard[player_two_y - 1][player_two_x - 1])

                if i == 3:
                    player_one_x = 1
                    player_two_x = 8
                    player_one_y += 1
                    player_two_y -= 1

                elif i == 7:
                    player_one_x = 2
                    player_two_x = 7
                    player_one_y += 1
                    player_two_y -= 1

                else:
                    player_one_x += 2
                    player_two_x -= 2

        else:
            input_array_position = 0
            for player in range(1, 3):
                for board_y in range(8):
                    for board_x in range(8):
                        if positions[input_array_position] > 0:
                            self.checkerboard[board_y][board_x]["checker"] = positions[input_array_position]
                            self.checkerboard[board_y][board_x]["player"] = player

                            if player == 1:
                                player_one_checkers.append(self.checkerboard[board_y][board_x])

                            if player == 2:
                                player_two_checkers.append(self.checkerboard[board_y][board_x])

                        input_array_position += 1

        self.all_checkers = [player_one_checkers, player_two_checkers]

    @staticmethod
    def switch_player(player):
        if player == 1:
            return 2

        return 1

    def print_board(self):
        for row in self.checkerboard:
            for position in row:
                print(position["position"], position["checker"], position["player"], end=" | ")

            print("\n")

    def get_neural_input(self):
        neural_inputs = []

        for row in self.checkerboard:
            for column in row:
                if column["player"] == 1:
                    neural_inputs.append(column["checker"])

                else:
                    neural_inputs.append(0.0)

        for row in self.checkerboard:
            for column in row:
                if column["player"] == 2:
                    neural_inputs.append(column["checker"])

                else:
                    neural_inputs.append(0.0)

        return neural_inputs

    def get_adaptive_input(self):
        neural_inputs = []

        for row in self.checkerboard:
            for column in row:
                if column["player"] == self.current_player:
                    neural_inputs.append(column["checker"])

                else:
                    neural_inputs.append(0.0)

        for row in self.checkerboard:
            for column in row:
                if column["player"] == self.switch_player(self.current_player):
                    neural_inputs.append(column["checker"])

                else:
                    neural_inputs.append(0.0)

        return neural_inputs

    def search_position(self, position, player):
        if player == 1:
            for index, checker in enumerate(self.all_checkers[0]):
                if checker["position"] == position:
                    return index

        else:
            for index, checker in enumerate(self.all_checkers[1]):
                if checker["position"] == position:
                    return index

        return None

    def get_number_checkers(self):
        return [len(self.all_checkers[0]), len(self.all_checkers[1])]

    @staticmethod
    def convert_position(position):
        column = ord(position[0]) - 97
        row = int(position[1]) - 1

        return [row, column]

    def move_checker(self, current_position, new_position, player):
        converted_current = self.convert_position(current_position)
        converted_new = self.convert_position(new_position)
        index = self.search_position(current_position, player)

        self.checkerboard[converted_new[0]][converted_new[1]]["checker"] = \
            self.checkerboard[converted_current[0]][converted_current[1]]["checker"]
        self.checkerboard[converted_new[0]][converted_new[1]]["player"] = \
            self.checkerboard[converted_current[0]][converted_current[1]]["player"]

        self.checkerboard[converted_current[0]][converted_current[1]]["checker"] = 0
        self.checkerboard[converted_current[0]][converted_current[1]]["player"] = 0
        self.checkerboard[converted_current[0]][converted_current[1]]["can_eat"] = False
        self.checkerboard[converted_current[0]][converted_current[1]]["can_move"] = True

        self.all_checkers[player - 1][index] = self.checkerboard[converted_new[0]][converted_new[1]]

        new_position_y = int(new_position[1])
        if player == 1 and self.all_checkers[player - 1][index]["checker"] == 0.5:
            if new_position_y == 8:
                self.all_checkers[player - 1][index]["checker"] = 1

        if player == 2 and self.all_checkers[player - 1][index]["checker"] == 0.5:
            if new_position_y == 1:
                self.all_checkers[player - 1][index]["checker"] = 1

    def set_can_eat(self, index, player):
        checker = self.all_checkers[player - 1][index]
        checker["can_eat"] = False
        current_x = ord(checker["position"][0])
        current_y = int(checker["position"][1])

        if player == 1 or checker["checker"] == 1:
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

                possibly_eaten_checker = self.search_position(right_front, self.switch_player(player))
                landing_space_player = self.search_position(right_landing, player)
                landing_space_opponent = self.search_position(right_landing, self.switch_player(player))

                if possibly_eaten_checker is not None and landing_space_player is None \
                        and landing_space_opponent is None:
                    checker["can_eat"] = True

            if left_landing_x > 96 and left_landing_y < 9:
                left_front = [str(chr(left_front_x)), str(left_front_y)]
                left_landing = [str(chr(left_landing_x)), str(left_landing_y)]

                possibly_eaten_checker = self.search_position(left_front, self.switch_player(player))
                landing_space_player = self.search_position(left_landing, player)
                landing_space_opponent = self.search_position(left_landing, self.switch_player(player))

                if possibly_eaten_checker is not None and landing_space_player is None \
                        and landing_space_opponent is None:
                    checker["can_eat"] = True

        if player == 2 or checker["checker"] == 1:
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

                possibly_eaten_checker = self.search_position(right_front, self.switch_player(player))
                landing_space_player = self.search_position(right_landing, player)
                landing_space_opponent = self.search_position(right_landing, self.switch_player(player))

                if possibly_eaten_checker is not None and landing_space_player is None \
                        and landing_space_opponent is None:
                    checker["can_eat"] = True

            if left_landing_x > 96 and left_landing_y > 0:
                left_front = [str(chr(left_front_x)), str(left_front_y)]
                left_landing = [str(chr(left_landing_x)), str(left_landing_y)]

                possibly_eaten_checker = self.search_position(left_front, self.switch_player(player))
                landing_space_player = self.search_position(left_landing, player)
                landing_space_opponent = self.search_position(left_landing, self.switch_player(player))

                if possibly_eaten_checker is not None and landing_space_player is None \
                        and landing_space_opponent is None:
                    checker["can_eat"] = True

    def find_all_can_eat(self, index, player, can_move, right_front_x, right_front_y, right_landing_x, right_landing_y,
                         left_front_x, left_front_y, left_landing_x, left_landing_y, step, direction):

        if direction == 1:
            current_position = [str(chr(right_front_x - 1)), str(right_front_y - 1)]
        else:
            current_position = [str(chr(right_front_x - 1)), str(right_front_y + 1)]

        right_front = [str(chr(right_front_x)), str(right_front_y)]
        right_landing = [str(chr(right_landing_x)), str(right_landing_y)]
        left_front = [str(chr(left_front_x)), str(left_front_y)]
        left_landing = [str(chr(left_landing_x)), str(left_landing_y)]

        right_checker = self.search_position(right_front, self.switch_player(player))
        left_checker = self.search_position(left_front, self.switch_player(player))

        right_friendly = self.search_position(right_front, player)
        left_friendly = self.search_position(left_front, player)

        if self.all_checkers[player - 1][index]["checker"] == 1 and step:
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

            right_back_checker = self.search_position(right_back, self.switch_player(player))
            left_back_checker = self.search_position(left_back, self.switch_player(player))

            if right_back_checker is not None and (left_front_x + 3) < 105 and 9 > int(right_back_landing[1]) > 0 \
                    and (len(can_move) == 0 or [right_back_landing, current_position] not in can_move) and \
                            [current_position, right_back_landing] not in can_move:
                landing_player = self.search_position(right_back_landing, player)
                landing_opponent = self.search_position(right_back_landing, self.switch_player(player))
                if (landing_player is None and landing_opponent is None) or \
                        (right_back_landing == self.all_checkers[player - 1][index][
                            "position"] and landing_player is not None and step):
                    can_move.append([current_position, right_back_landing])

                    if direction == 1:
                        if left_front_y - 4 > 0:
                            self.find_all_can_eat(index, player, can_move, ord(right_back_landing[0]) + 1,
                                                  int(right_back_landing[1]) - 1,
                                                  ord(right_back_landing[0]) + 2, int(right_back_landing[1]) - 2,
                                                  ord(right_back_landing[0]) - 1, int(right_back_landing[1]) - 1,
                                                  ord(right_back_landing[0]) - 2, int(right_back_landing[1]) - 2, True,
                                                  2)

                    if direction == 2:
                        if left_front_y + 4 < 9:
                            self.find_all_can_eat(index, player, can_move, ord(right_back_landing[0]) + 1,
                                                  int(right_back_landing[1]) + 1,
                                                  ord(right_back_landing[0]) + 2, int(right_back_landing[1]) + 2,
                                                  ord(right_back_landing[0]) - 1, int(right_back_landing[1]) + 1,
                                                  ord(right_back_landing[0]) - 2, int(right_back_landing[1]) + 2, True,
                                                  1)

            if left_back_checker is not None and (right_front_x - 3) > 96 and 9 > int(left_back_landing[1]) > 0 \
                    and (len(can_move) == 0 or [left_back_landing, current_position] not in can_move) and \
                            [current_position, left_back_landing] not in can_move:
                landing_player = self.search_position(left_back_landing, player)
                landing_opponent = self.search_position(left_back_landing, self.switch_player(player))

                if landing_player is None and landing_opponent is None or \
                        (left_back_landing == self.all_checkers[player - 1][index][
                            "position"] and landing_player is not None and step):
                    can_move.append([current_position, left_back_landing])

                    if direction == 1:
                        if right_front_y - 4 > 0:
                            self.find_all_can_eat(index, player, can_move, ord(left_back_landing[0]) + 1,
                                                  int(left_back_landing[1]) - 1,
                                                  ord(left_back_landing[0]) + 2, int(left_back_landing[1]) - 2,
                                                  ord(left_back_landing[0]) - 1, int(left_back_landing[1]) - 1,
                                                  ord(left_back_landing[0]) - 2, int(left_back_landing[1]) - 2, True,
                                                  2)

                    if direction == 2:
                        if right_front_y + 4 < 9:
                            self.find_all_can_eat(index, player, can_move, ord(left_back_landing[0]) + 1,
                                                  int(left_back_landing[1]) + 1,
                                                  ord(left_back_landing[0]) + 2, int(left_back_landing[1]) + 2,
                                                  ord(left_back_landing[0]) - 1, int(left_back_landing[1]) + 1,
                                                  ord(left_back_landing[0]) - 2, int(left_back_landing[1]) + 2, True,
                                                  1)

        if right_checker is None and left_checker is None and right_friendly is None and left_friendly is None:
            if not step:
                if right_front_x < 105:
                    can_move.append([self.all_checkers[player - 1][index]["position"], right_front])

                if left_front_x > 96:
                    can_move.append([self.all_checkers[player - 1][index]["position"], left_front])
                return

            return

        if right_checker is None and right_friendly is None and not step:
            can_move.append([self.all_checkers[player - 1][index]["position"], right_front])

        if left_checker is None and left_friendly is None and not step:
            can_move.append([self.all_checkers[player - 1][index]["position"], left_front])

        if right_checker is not None and right_landing_x < 105 and 9 > right_landing_y > 0 \
                and (len(can_move) == 0 or [right_landing, current_position] not in can_move) and \
                        [current_position, right_landing] not in can_move:
            landing_space_player = self.search_position(right_landing, player)
            landing_space_opponent = self.search_position(right_landing, self.switch_player(player))

            if landing_space_player is None and landing_space_opponent is None or \
                    (right_landing == self.all_checkers[player - 1][index][
                        "position"] and landing_space_player is not None and step):
                can_move.append([current_position, right_landing])

                if direction == 1:
                    if right_landing_y + 1 < 9:
                        self.find_all_can_eat(index, player, can_move, right_landing_x + 1, right_landing_y + 1,
                                              right_landing_x + 2,
                                              right_landing_y + 2, right_landing_x - 1, right_landing_y + 1,
                                              right_landing_x - 2, right_landing_y + 2, True, 1)

                if direction == 2:
                    if right_landing_y - 1 > 0:
                        self.find_all_can_eat(index, player, can_move, right_landing_x + 1, right_landing_y - 1,
                                              right_landing_x + 2,
                                              right_landing_y - 2, right_landing_x - 1, right_landing_y - 1,
                                              right_landing_x - 2, right_landing_y - 2, True, 2)

        if left_checker is not None and left_landing_x > 96 and 9 > left_landing_y > 0 \
                and (len(can_move) == 0 or [left_landing, current_position] not in can_move) and \
                        [current_position, left_landing] not in can_move:
            landing_space_player = self.search_position(left_landing, player)
            landing_space_opponent = self.search_position(left_landing, self.switch_player(player))

            if landing_space_player is None and landing_space_opponent is None or \
                    (left_landing == self.all_checkers[player - 1][index][
                        "position"] and landing_space_player is not None and step):
                can_move.append([current_position, left_landing])

                if direction == 1:
                    if left_landing_y + 1 < 9:
                        self.find_all_can_eat(index, player, can_move, left_landing_x + 1, left_landing_y + 1,
                                              left_landing_x + 2,
                                              left_landing_y + 2, left_landing_x - 1, left_landing_y + 1,
                                              left_landing_x - 2,
                                              left_landing_y + 2, True, 1)

                if direction == 2:
                    if left_landing_y - 1 > 0:
                        self.find_all_can_eat(index, player, can_move, left_landing_x + 1, left_landing_y - 1,
                                              left_landing_x + 2,
                                              left_landing_y - 2, left_landing_x - 1, left_landing_y - 1,
                                              left_landing_x - 2,
                                              left_landing_y - 2, True, 2)

        return

    def get_movements(self, index, player):
        checker = self.all_checkers[player - 1][index]
        can_move = []
        current_x = ord(checker["position"][0])
        current_y = int(checker["position"][1])

        if player == 1 or checker["checker"] == 1:
            right_front_x = current_x + 1
            right_front_y = current_y + 1
            right_landing_x = right_front_x + 1
            right_landing_y = right_front_y + 1

            left_front_x = current_x - 1
            left_front_y = current_y + 1
            left_landing_x = left_front_x - 1
            left_landing_y = left_front_y + 1

            if (right_front_x < 105 and right_front_y < 9) or (left_front_x > 96 and left_front_y < 9):
                self.find_all_can_eat(index, player, can_move, right_front_x, right_front_y, right_landing_x,
                                      right_landing_y,
                                      left_front_x, left_front_y, left_landing_x, left_landing_y, False, 1)

        if player == 2 or checker["checker"] == 1:
            right_front_x = current_x + 1
            right_front_y = current_y - 1
            right_landing_x = right_front_x + 1
            right_landing_y = right_front_y - 1

            left_front_x = current_x - 1
            left_front_y = current_y - 1
            left_landing_x = left_front_x - 1
            left_landing_y = left_front_y - 1

            if (right_front_x < 105 and right_front_y > 0) or (left_front_x > 96 and left_front_y > 0):
                self.find_all_can_eat(index, player, can_move, right_front_x, right_front_y, right_landing_x,
                                      right_landing_y,
                                      left_front_x, left_front_y, left_landing_x, left_landing_y, False, 2)

        return can_move

    def movable(self, index, player):
        checker = self.all_checkers[player - 1][index]
        current_x = ord(checker["position"][0])
        current_y = int(checker["position"][1])

        self.set_can_eat(index, player)
        movable_front = True
        movable_back = True

        if player == 1 or checker["checker"] == 1:
            right_front_x = current_x + 1
            right_front_y = current_y + 1
            left_front_x = current_x - 1
            left_front_y = current_y + 1

            right_front = [str(chr(right_front_x)), str(right_front_y)]
            left_front = [str(chr(left_front_x)), str(left_front_y)]

            if current_y + 1 >= 9:
                checker["can_move"] = False
                movable_front = False

            if right_front_x >= 105 and not checker["can_eat"]:
                left = self.search_position(left_front, player)
                left_friendly = self.search_position(left_front, self.switch_player(player))
                if left is not None or left_friendly is not None:
                    checker["can_move"] = False
                    movable_front = False

            if left_front_x <= 96 and not checker["can_eat"]:
                right = self.search_position(right_front, player)
                right_friendly = self.search_position(right_front, self.switch_player(player))
                if right is not None or right_friendly is not None:
                    checker["can_move"] = False
                    movable_front = False

            if not checker["can_eat"]:
                right = self.search_position(right_front, player)
                right_friendly = self.search_position(right_front, self.switch_player(player))
                if right is not None or right_friendly is not None:
                    left = self.search_position(left_front, player)
                    left_friendly = self.search_position(left_front, self.switch_player(player))
                    if left is not None or left_friendly is not None:
                        checker["can_move"] = False
                        movable_front = False

        if player == 2 or checker["checker"] == 1:
            right_front_x = current_x + 1
            right_front_y = current_y - 1
            left_front_x = current_x - 1
            left_front_y = current_y - 1

            right_front = [str(chr(right_front_x)), str(right_front_y)]
            left_front = [str(chr(left_front_x)), str(left_front_y)]

            if current_y - 1 <= 0:
                checker["can_move"] = False
                movable_back = False

            if right_front_x >= 105 and not checker["can_eat"]:
                left = self.search_position(left_front, player)
                left_friendly = self.search_position(left_front, self.switch_player(player))
                if left is not None or left_friendly is not None:
                    checker["can_move"] = False
                    movable_back = False

            if left_front_x <= 96 and not checker["can_eat"]:
                right = self.search_position(right_front, player)
                right_friendly = self.search_position(right_front, self.switch_player(player))
                if right is not None or right_friendly is not None:
                    checker["can_move"] = False
                    movable_back = False

            if not checker["can_eat"]:
                right = self.search_position(right_front, player)
                right_friendly = self.search_position(right_front, self.switch_player(player))
                if right is not None or right_friendly is not None:
                    left = self.search_position(left_front, player)
                    left_friendly = self.search_position(left_front, self.switch_player(player))
                    if left is not None or left_friendly is not None:
                        checker["can_move"] = False
                        movable_back = False

        if player == 1 and checker["checker"] == 0.5:
            if movable_front:
                checker["can_move"] = True

        if player == 2 and checker["checker"] == 0.5:
            if movable_back:
                checker["can_move"] = True

        if checker["checker"] == 1:
            if movable_front or movable_back:
                checker["can_move"] = True

    @staticmethod
    def has_next_movement(movement_array, current_position):
        for index, movement in enumerate(movement_array):
            if movement[0] == current_position[1]:
                return index

        return -1

    def sort_movements(self, index, player, movement_array):
        different_movements = []

        checker = self.all_checkers[player - 1][index]
        current_x = ord(checker["position"][0])
        current_y = int(checker["position"][1])

        left_front = []
        right_front = []

        if (player == 1 and checker["can_eat"]) or (checker["checker"] == 1 and checker["can_eat"]):
            left_front = [checker["position"], [str(chr(current_x - 1)), str(current_y + 1)]]
            right_front = [checker["position"], [str(chr(current_x + 1)), str(current_y + 1)]]

            try:
                movement_array.remove(left_front)
            except ValueError:
                pass

            try:
                movement_array.remove(right_front)
            except ValueError:
                pass

        if (player == 2 and checker["can_eat"]) or (checker["checker"] == 1 and checker["can_eat"]):
            left_front = [checker["position"], [str(chr(current_x - 1)), str(current_y - 1)]]
            right_front = [checker["position"], [str(chr(current_x + 1)), str(current_y - 1)]]

            try:
                movement_array.remove(left_front)
            except ValueError:
                pass

            try:
                movement_array.remove(right_front)
            except ValueError:
                pass

        if not checker["can_eat"]:
            if player == 1 or checker["checker"] == 1:
                left_front_search = [str(chr(current_x - 1)), str(current_y + 1)]
                right_front_search = [str(chr(current_x + 1)), str(current_y + 1)]

                if self.search_position(left_front_search, player) is not None:
                    try:
                        movement_array.remove(left_front)
                    except ValueError:
                        pass

                if self.search_position(right_front_search, player) is not None:
                    try:
                        movement_array.remove(right_front)
                    except ValueError:
                        pass

            if player == 2 or checker["checker"] == 1:
                left_front_search = [str(chr(current_x - 1)), str(current_y - 1)]
                right_front_search = [str(chr(current_x + 1)), str(current_y - 1)]

                if self.search_position(left_front_search, player) is not None:
                    try:
                        movement_array.remove(left_front)
                    except ValueError:
                        pass

                if self.search_position(right_front_search, player) is not None:
                    try:
                        movement_array.remove(right_front)
                    except ValueError:
                        pass

        for movement in movement_array:
            if movement[0] == checker["position"]:
                different_movements.append([movement])

        for movement in different_movements:
            index = self.has_next_movement(movement_array, movement[len(movement) - 1])
            while index != -1:
                movement.append(movement_array[index])
                index = self.has_next_movement(movement_array, movement[len(movement) - 1])
                if index != -1 and movement_array[index] in movement:
                    index = -1

        if checker["can_eat"]:

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

    def check_if_trapped(self):
        player_checkers = self.all_checkers[self.current_player - 1]
        if len(player_checkers) == 0:
            return False

        for checker in player_checkers:
            if checker["can_move"]:
                return False

        return True

    def check_can_eat(self, player):
        player_checkers = self.all_checkers[player - 1]
        for checker in player_checkers:
            if checker["can_eat"]:
                return True

        return False

    def eat_checker(self, position, player_belonged):
        to_be_eaten = self.search_position(position, player_belonged)

        if to_be_eaten is not None:
            converted_current = self.convert_position(position)
            self.checkerboard[converted_current[0]][converted_current[1]]["checker"] = 0
            self.checkerboard[converted_current[0]][converted_current[1]]["player"] = 0
            self.checkerboard[converted_current[0]][converted_current[1]]["can_eat"] = False
            self.checkerboard[converted_current[0]][converted_current[1]]["can_move"] = True
            del self.all_checkers[player_belonged - 1][to_be_eaten]

    def get_checkers_can_eat(self, player):
        checkers = []
        player_checkers = self.all_checkers[player - 1]

        for checker in player_checkers:
            if checker["can_eat"]:
                checkers.append(checker)

        return checkers

    def get_checkers_can_move(self, player):
        checkers = []
        player_checkers = self.all_checkers[player - 1]

        for checker in player_checkers:
            if checker["can_move"]:
                checkers.append(checker)

        return checkers

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

    def set_player_one_ai(self, mind):
        self.player_one_ai = mind

    def set_player_two_ai(self, mind):
        self.player_two_ai = mind

    def reset_board(self, neural_input=None):
        if neural_input is None:
            self.__init__()

        else:
            self.__init__(neural_input)

    def start_game(self):

        overall_rating = 0

        if self.player_one_ai is not None and self.player_two_ai is not None:

            for index in range(len(self.all_checkers[self.current_player - 1])):
                self.movable(index, self.current_player)

            while not self.check_if_trapped() and len(self.all_checkers[self.current_player - 1]) > 0:

                if self.current_player == 1:
                    self.player_one_ai.make_move()

                else:
                    self.player_two_ai.make_move()

                for index in range(len(self.all_checkers[self.current_player - 1])):
                    self.movable(index, self.current_player)

            if self.current_player == 1:
                self.player_two_ai.is_winner = True

            if self.current_player == 2:
                self.player_one_ai.is_winner = True

            stats = self.predictor_ai.get_stats()

            if self.predictor_ai.is_winner:
                overall_rating += 50

            if 30 >= stats[0] > 20:
                overall_rating += 10

            if 20 >= stats[0] > 15:
                overall_rating += 15

            if 15 >= stats[0] > 10:
                overall_rating += 20

            if stats[0] <= 10:
                overall_rating += 30

            overall_rating += stats[1] * 2
            overall_rating += stats[2] * 2
            overall_rating += stats[3] * 3

        return overall_rating

    def start_game_base_brain(self):

        if self.player_one_ai is not None and self.player_two_ai is not None:

            for index in range(len(self.all_checkers[self.current_player - 1])):
                self.movable(index, self.current_player)

            while not self.check_if_trapped() and len(self.all_checkers[self.current_player - 1]) > 0:

                if self.current_player == 1:
                    self.player_one_ai.make_move()

                else:
                    self.player_two_ai.make_move()

                for index in range(len(self.all_checkers[self.current_player - 1])):
                    self.movable(index, self.current_player)

            if self.current_player == 1:
                self.player_two_ai.is_winner = True

            if self.current_player == 2:
                self.player_one_ai.is_winner = True

            fitness_one = 0
            fitness_two = 0

            if self.player_one_ai.is_winner:
                fitness_one += 50

            if self.player_two_ai.is_winner:
                fitness_two += 50

            stats = self.player_one_ai.get_stats()
            if self.check_if_trapped() and self.current_player == 2:
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

            stats = self.player_two_ai.get_stats()
            if self.check_if_trapped() and self.current_player == 1:
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

    def __init__(self, checkerboard, player, brain=None, adaptive_brain=None, chromosome_brain=None):
        self.player = player
        self.checker_side = checkerboard.all_checkers[player - 1]
        self.board = checkerboard
        self.number_checkers_left = len(self.checker_side)
        self.number_of_turns_passed = 0
        self.number_of_kings = 0
        self.checker_eaten = 0
        self.was_king = False
        self.base_brain = []
        self.brain = []
        self.genome = None
        self.adaptive_brain = None

        if adaptive_brain is not None:
            self.adaptive_brain = adaptive_brain

        self.is_winner = False

        if brain is None:
            self.make_brain()

        else:
            self.base_brain = brain

        if chromosome_brain is not None:
            self.update_brain(chromosome_brain)

        self.brain = copy.deepcopy(self.base_brain)

    def set_base_brain(self, base_brain):
        self.base_brain = base_brain
        self.brain = copy.deepcopy(self.base_brain)

    def get_movable_checkers(self):
        movable_checkers = []
        for index, checker in enumerate(self.checker_side):
            if checker["can_move"]:
                movable_checkers.append(index)

        return movable_checkers

    def get_checkers_can_eat(self):
        can_eat_checkers = []
        for index, checker in enumerate(self.checker_side):
            if checker["can_eat"]:
                can_eat_checkers.append(index)

        return can_eat_checkers

    def get_single_movable_position(self, index):
        movement_array = self.board.get_movements(index, self.player)
        movement_array = self.board.sort_movements(index, self.player, movement_array)
        movable_positions = []
        for movement in movement_array:
            for direction in movement:
                movable_positions.append(direction[1])

        return movable_positions

    @staticmethod
    def is_multi_directional(position, multi_directional):
        if multi_directional:
            for index, multi_position in enumerate(multi_directional):
                if position[1] == multi_position[0]:
                    return index

        return -1

    def get_multi_destinations(self, movement, multi_directional, destinations, path, count):
        index = Checkerboard.has_next_movement(movement, path[len(path) - 1])
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
                if self.checker_side[checker]["position"] == rank["position"]:
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
        for c in range(len(self.checker_side)):
            self.board.movable(c, self.player)

        can_eat = self.get_checkers_can_eat()

        if len(can_eat) > 0:
            selected_checker = self.select_checker_or_movement(can_eat, None, None)
            movement_array = self.board.get_movements(selected_checker, self.player)
            movement_array = self.board.sort_movements(selected_checker, self.player, movement_array)
            sort = self.sort_eating_movements([movement_array])
            if self.adaptive_brain is not None:
                inputs = self.board.get_adaptive_input()
                adaptations = self.adaptive_brain.activate(inputs)
                self.adapt_situation(adaptations)
            path = self.select_checker_or_movement(None, None, sort)
            selected_checker = self.board.search_position(path[0][0], self.player)

            if self.checker_side[selected_checker]["checker"] == 1:
                self.was_king = True

            destination = None
            for movement in path:
                destination = movement[1]
                checker_to_be_eaten = self.board.position_to_be_eaten(self.checker_side[selected_checker]["position"],
                                                                      destination)

                self.board.move_checker(self.checker_side[selected_checker]["position"], destination, self.player)
                self.board.eat_checker(checker_to_be_eaten, self.board.switch_player(self.player))

            selected_checker = self.board.search_position(destination, self.player)
            if self.checker_side[selected_checker]["checker"] == 1 and not self.was_king:
                self.number_of_kings += 1

            self.checker_eaten += len(path)

        else:
            movable_checkers = self.get_movable_checkers()
            if self.adaptive_brain is not None:
                inputs = self.board.get_adaptive_input()
                adaptations = self.adaptive_brain.activate(inputs)
                self.adapt_situation(adaptations)
            selected_checker = self.select_checker_or_movement(movable_checkers, None, None)

            if self.checker_side[selected_checker]["checker"] == 1:
                self.was_king = True

            movements = self.get_single_movable_position(selected_checker)
            selected_destination = self.select_checker_or_movement(None, movements, None)

            self.board.move_checker(self.checker_side[selected_checker]["position"], selected_destination, self.player)

            selected_checker = self.board.search_position(selected_destination, self.player)
            if self.checker_side[selected_checker]["checker"] == 1 and not self.was_king:
                self.number_of_kings += 1

        self.board.current_player = self.board.switch_player(self.player)
        self.number_checkers_left = len(self.checker_side)
        self.number_of_turns_passed += 1
        self.was_king = False

    def get_stats(self):
        return [self.number_of_turns_passed, self.number_checkers_left, self.checker_eaten, self.number_of_kings]

    def make_brain(self):
        for i in range(ord("a"), ord("i")):
            for j in range(1, 9):
                self.base_brain.append(
                    {"position": [str(chr(i)), str(j)], "movement_rank": numpy.random.uniform(0, 1),
                     "checker_rank": numpy.random.uniform(0, 1)})

    def list_all_moves(self):
        all_moves = {"can_eat": False, "moves": []}

        for c in range(len(self.checker_side)):
            self.board.movable(c, self.player)

        can_eat = self.get_checkers_can_eat()

        if len(can_eat) > 0:
            all_moves["can_eat"] = True
            for selected_checker in can_eat:
                movement_array = self.board.get_movements(selected_checker, self.player)
                movement_array = self.board.sort_movements(selected_checker, self.player, movement_array)
                sort = self.sort_eating_movements([movement_array])
                for move in sort:
                    all_moves["moves"].append(move[2])

        else:
            movable_checkers = self.get_movable_checkers()
            for selected_checker in movable_checkers:
                movements = self.get_single_movable_position(selected_checker)
                for movement in movements:
                    movement_x = ord(movement[0])
                    movement_y = int(movement[1])

                    if 105 > movement_x > 96 and 9 > movement_y > 0:
                        all_moves["moves"].append([self.checker_side[selected_checker]["position"], movement])

        return all_moves


def get_input(neural_input):
    print(neural_input)
    checkerboard = Checkerboard(neural_input)
    checkerboard.print_board()


def get_prediction(neural_input, player, brain, adaptive_brain):
    checkerboard = Checkerboard(neural_input)
    checkerboard.current_player = checkerboard.switch_player(player)  # move will already be made by current player when
    # the start_game function is called.
    player_one = Mind(checkerboard, 1, brain, adaptive_brain)
    player_two = Mind(checkerboard, 2, brain, adaptive_brain)
    checkerboard.set_player_one_ai(player_one)
    checkerboard.set_player_two_ai(player_two)

    if player == 1:
        checkerboard.predictor_ai = player_one

    else:
        checkerboard.predictor_ai = player_two

    checker_moves = checkerboard.predictor_ai.list_all_moves()
    # print(checker_moves)
    rated_moves = []

    if checker_moves["can_eat"]:

        for path in checker_moves["moves"]:
            selected_checker = checkerboard.search_position(path[0][0], player)

            for movement in path:
                destination = movement[1]
                checker_to_be_eaten = checkerboard.position_to_be_eaten(
                    checkerboard.all_checkers[player - 1][selected_checker]["position"],
                    destination)

                checkerboard.move_checker(checkerboard.all_checkers[player - 1][selected_checker]["position"],
                                          destination, player)
                checkerboard.eat_checker(checker_to_be_eaten, checkerboard.switch_player(player))

            rating = checkerboard.start_game()
            rated_move = {"can_eat": True, "move": path, "rating": rating}
            rated_moves.append(rated_move)

            checkerboard.reset_board(neural_input)
            checkerboard.current_player = checkerboard.switch_player(player)
            player_one = Mind(checkerboard, 1, brain, adaptive_brain)
            player_two = Mind(checkerboard, 2, brain, adaptive_brain)
            checkerboard.set_player_one_ai(player_one)
            checkerboard.set_player_two_ai(player_two)

            if player == 1:
                checkerboard.predictor_ai = player_one

            else:
                checkerboard.predictor_ai = player_two

    else:

        for movement in checker_moves["moves"]:

            checkerboard.move_checker(movement[0], movement[1], player)

            rating = checkerboard.start_game()
            rated_move = {"can_eat": False, "move": movement, "rating": rating}
            rated_moves.append(rated_move)

            checkerboard.reset_board(neural_input)
            checkerboard.current_player = checkerboard.switch_player(player)
            player_one = Mind(checkerboard, 1, brain, adaptive_brain)
            player_two = Mind(checkerboard, 2, brain, adaptive_brain)
            checkerboard.set_player_one_ai(player_one)
            checkerboard.set_player_two_ai(player_two)

            if player == 1:
                checkerboard.predictor_ai = player_one

            else:
                checkerboard.predictor_ai = player_two

    highest_rating = 0
    highest_rated_move = None
    for move_rated in rated_moves:
        if move_rated["rating"] > highest_rating:
            highest_rating = move_rated["rating"]
            highest_rated_move = move_rated

    return highest_rated_move


def start_match(chromosome_brain_one, chromosome_brain_two, player):
    checkerboard = Checkerboard()

    player_one_ai = Mind(checkerboard, 1, chromosome_brain=chromosome_brain_one)
    player_two_ai = Mind(checkerboard, 2, chromosome_brain=chromosome_brain_two)

    checkerboard.set_player_one_ai(player_one_ai)
    checkerboard.set_player_two_ai(player_two_ai)

    fitness = checkerboard.start_game_base_brain()
    winner = [player_one_ai.is_winner, player_two_ai.is_winner]

    return [winner[player-1], fitness[player-1]]


def get_brain(winning_chromosome_brain):
    checkerboard = Checkerboard()
    brain_creator = Mind(checkerboard, 1, chromosome_brain=winning_chromosome_brain)

    brain = brain_creator.base_brain
    return brain