import unittest
import task_manager


class SignalingTaskTestCase(unittest.TestCase):

    def test_signaling_task(self):
        SignalingTask = task_manager.get_signaling_task_class(task_manager.Task)

        st = SignalingTask()

        attr_results = {}
        @st.on_set.connect
        def on_set(sender, **kwargs):
            attr_results[kwargs.get('attr')] = kwargs.get('value')

        for prop in st._task_properties:
            setattr(st, prop, "%s_test" % prop)
            assert attr_results[prop] == getattr(st, prop)

if __name__ == "__main__":
    unittest.main()
