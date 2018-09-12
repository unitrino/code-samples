class Elevator:
    current_direction = "UP"
    current_stage = 0
    stage_up = {}
    stage_down = {}
    to_visit_floor = []
    endpoint_floor = -1

    def __init__(self, elevator_control):
        self.__elevator_control = elevator_control

    # кнопка на площадке нажата
    def push_new_button(self, button):
        floor = button.floor
        direction = button.direction
        if direction == "UP":
            self.stage_up[floor] = True
        else:
            self.stage_down[floor] = True

    # нажата кнопка в лифте
    def push_button_in_elevator(self, pushed_floor):
        self.to_visit_floor.append(pushed_floor)
        if self.current_direction == "UP":
            self.endpoint_floor = max(self.endpoint_floor, pushed_floor)
        else:
            self.endpoint_floor = min(self.endpoint_floor, pushed_floor)
        self.__elevator_control.go(self.endpoint_floor)

    # Двери лифта закрываються и лифт в простое
    def stop_event(self):
        if self.stage_up:
            self.endpoint_floor, self.current_direction = self.stage_up.popitem()
            self.__elevator_control.go(self.endpoint_floor)
        elif self.stage_down:
            self.endpoint_floor, self.current_direction = self.stage_down.popitem()
            self.__elevator_control.go(self.endpoint_floor)

    # Мы остановились на этаже
    def visit_floor(self, floor):
        if self.current_direction == "UP":
            self.stage_up.pop(floor)
        else:
            self.stage_down.pop(floor)
        self.to_visit_floor.remove(floor)


    # Нужно ли остановиться на этаже
    def is_stop(self, to_floor):
        if self.current_direction == "UP":
            if to_floor in self.stage_up:
                return True
        else:
            if to_floor in self.stage_down:
                return True

        if to_floor in self.to_visit_floor:
            return True
