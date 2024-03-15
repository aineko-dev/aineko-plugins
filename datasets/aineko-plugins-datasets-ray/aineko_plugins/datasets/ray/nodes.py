# Copyright 2023 Aineko Authors
# SPDX-License-Identifier: Apache-2.0
import time

from aineko import AbstractNode


class TestReader(AbstractNode):
    def _execute(self, params):
        try:
            msg = self.inputs["ray_dataset"].read()
            if msg:
                print(type(msg))
                print(msg)
        except Exception as e:
            print(e)
        time.sleep(5)


class TestWriter(AbstractNode):
    def _pre_loop_hook(self, params: dict) -> None:
        self.counter = 0

    def _execute(self, params):
        try:
            self.outputs["ray_dataset"].write(
                {"message": f"Hello {self.counter}"}
            )
            self.counter += 1
        except Exception as e:
            print(e)
        time.sleep(5)
