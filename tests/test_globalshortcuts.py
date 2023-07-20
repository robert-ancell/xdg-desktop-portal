# SPDX-License-Identifier: LGPL-2.1-or-later
#
# This file is formatted with Python Black


from tests import Request, PortalTest, Session
from gi.repository import GLib

import dbus
import socket


class TestGlobalShortcuts(PortalTest):
    def test_version(self):
        self.check_version(1)

    def test_global_shortcuts_create_close_session(self):
        self.start_impl_portal()
        self.start_xdp()

        gs_intf = self.get_dbus_interface()
        request = Request(self.dbus_con, gs_intf)
        options = {
            "session_handle_token": "session_token0",
        }
        response = request.call(
            "CreateSession",
            options=options,
        )

        assert response.response == 0

        session = Session.from_response(self.dbus_con, response)
        # Check the impl portal was called with the right args
        method_calls = self.mock_interface.GetMethodCalls("CreateSession")
        assert len(method_calls) > 0
        _, args = method_calls[-1]
        assert args[1] == session.handle
        assert args[2] == ""  # appid

        session.close()

        mainloop = GLib.MainLoop()
        GLib.timeout_add(2000, mainloop.quit)
        mainloop.run()

        assert session.closed

    def test_global_shortcuts_create_session_signal_closed(self):
        params = {"force-close": 500}
        self.start_impl_portal(params=params)
        self.start_xdp()

        gs_intf = self.get_dbus_interface()
        request = Request(self.dbus_con, gs_intf)
        options = {
            "session_handle_token": "session_token0",
        }
        response = request.call(
            "CreateSession",
            options=options,
        )

        assert response.response == 0

        session = Session.from_response(self.dbus_con, response)
        # Check the impl portal was called with the right args
        method_calls = self.mock_interface.GetMethodCalls("CreateSession")
        assert len(method_calls) > 0
        _, args = method_calls[-1]
        assert args[1] == session.handle
        assert args[2] == ""  # appid

        # Now expect the backend to close it

        mainloop = GLib.MainLoop()
        GLib.timeout_add(2000, mainloop.quit)
        mainloop.run()

        assert session.closed

    def test_global_shortcuts_bind_list_shortcuts(self):
        self.start_impl_portal()
        self.start_xdp()

        gs_intf = self.get_dbus_interface()
        request = Request(self.dbus_con, gs_intf)
        options = {
            "session_handle_token": "session_token0",
        }
        response = request.call(
            "CreateSession",
            options=options,
        )

        assert response.response == 0

        session = Session.from_response(self.dbus_con, response)

        shortcuts = [
            (
                "binding1",
                {
                    "description": dbus.String("Binding #1", variant_level=1),
                    "preferred-trigger": dbus.String("CTRL+a", variant_level=1),
                },
            ),
            (
                "binding2",
                {
                    "description": dbus.String("Binding #2", variant_level=1),
                    "preferred-trigger": dbus.String("CTRL+b", variant_level=1),
                },
            ),
        ]

        request = Request(self.dbus_con, gs_intf)
        response = request.call(
            "BindShortcuts",
            session_handle=session.handle,
            shortcuts=shortcuts,
            parent_window="",
            options={},
        )

        request = Request(self.dbus_con, gs_intf)
        options = {}
        response = request.call(
            "ListShortcuts",
            session_handle=session.handle,
            options=options,
        )

        assert len(list(actual_shortcuts)) == len(list(shortcuts))

        session.close()

        mainloop = GLib.MainLoop()
        GLib.timeout_add(2000, mainloop.quit)
        mainloop.run()

        assert session.closed