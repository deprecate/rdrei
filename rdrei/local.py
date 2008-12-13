from werkzeug import Local, LocalManager

local = Local()
local_manager = LocalManager([local])

