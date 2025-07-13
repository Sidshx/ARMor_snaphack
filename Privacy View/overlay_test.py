import win32gui
import win32con
import win32api
import time

className = "TestOpaque"
hInstance = win32api.GetModuleHandle()
wndClass = win32gui.WNDCLASS()
wndClass.lpfnWndProc = win32gui.DefWindowProc
wndClass.hInstance = hInstance
wndClass.lpszClassName = className
win32gui.RegisterClass(wndClass)

hwnd = win32gui.CreateWindowEx(
    win32con.WS_EX_TOPMOST,
    className,
    "VISIBLE TEST",
    win32con.WS_POPUP,
    100, 100, 300, 200,
    None, None, hInstance, None
)

win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 100, 100, 300, 200, 0)
win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
time.sleep(5)
win32gui.DestroyWindow(hwnd)
