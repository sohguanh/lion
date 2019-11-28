import logging
import threading
import datetime as dt


class SlidingWindowTuple:
    def __init__(self, count, minute_mark):
        self.count = count
        self.minute_mark = minute_mark

    def get_count(self):
        return self.count

    def get_minute_mark(self):
        return self.minute_mark

    def set_count(self, count):
        self.count = count

    def set_minute_mark(self, minute_mark):
        self.minute_mark = minute_mark


class SlidingWindow:
    def __init__(self, request_per_min=30):
        '''
        request_per_min parameter to indicate how many request the url endpoint can handle per minute before rejecting.
        '''
        self.request_per_min = request_per_min
        self.list = []
        self.lock = threading.Lock()

    def is_allowed(self) -> bool:
        self.lock.acquire()
        allowed = self.__ok()
        self.lock.release()
        return allowed

    def __weight_formula(self, prev_counter, curr_minute_mark_pct, curr_counter) -> int:
        return int(float(prev_counter)*(1.-curr_minute_mark_pct)) + curr_counter

    def __ok(self) -> bool:
        curr_date = dt.datetime.today()
        curr_min = curr_date.minute
        curr_sec = curr_date.second
        cnt = len(self.list)
        if cnt == 0:
            self.list.append(SlidingWindowTuple(1, curr_min))
            return True
        elif cnt <= 2:
            logging.debug("cnt: "+str(cnt))
            front = self.list[0]
            if front.get_minute_mark() == curr_min:  # within same bucket
                logging.debug("within same bucket")
                if cnt == 2:  # check previous bucket apply formula
                    back = self.list[1]
                    if self.__weight_formula(back.get_count(), float(curr_sec/60), front.get_count()) > self.request_per_min:
                        logging.debug("within same bucket reject 0")
                        return False

                new_count = front.get_count() + 1
                if new_count > self.request_per_min:
                    logging.debug("within same bucket reject 1 with new_count "+str(new_count))
                    return False
                else:
                    front.set_count(new_count)
                    return True
            else:  # not found in current bucket
                logging.debug("not same bucket")
                prev_minute_mark = curr_min - 1
                if curr_min == 0:
                    prev_minute_mark = 59
                if front.get_minute_mark() == prev_minute_mark:
                    # check if allowed using weightFormula
                    if self.__weight_formula(front.get_count(), float(curr_sec/60), 0) > self.request_per_min:
                        logging.debug("not same bucket reject 0")
                        return False
                    else:
                        if cnt == 1:
                            # if cnt == 1 add new bucket in front
                            self.list.insert(0, SlidingWindowTuple(1, curr_min))
                        elif cnt == 2:
                            # if cnt == 2
                            # copy front bucket to back bucket
                            # overwrite front bucket with new counter value
                            back = self.list[1]

                            back.set_count(front.get_count())
                            back.set_minute_mark(front.get_minute_mark())

                            front.set_count(1)
                            front.set_minute_mark(curr_min)
                        return True
                else:
                    if cnt == 1:
                        # if cnt == 1 > 1 min interval so just overwrite front bucket with new counter value
                        front.set_count(1)
                        front.set_minute_mark(curr_min)
                    elif cnt == 2:
                        # if cnt == 2 > 1 min interval so just overwrite front bucket with new counter value
                        # remove the back bucket as not needed for compare anymore
                        front.set_count(1)
                        front.set_minute_mark(curr_min)

                        self.list.pop()
                    return True

        logging.debug("outside reject 999")
        return False  # not supposed to come here but if it does return false by default
