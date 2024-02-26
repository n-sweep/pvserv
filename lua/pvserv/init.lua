local vim = vim


function PVServ()
    local M = {}

    local to_load = {
        'pvserv.assets'
    }

    -- load all dependencies in `to_load` into the module
    for _, tbl in ipairs(to_load) do
        local t = require(tbl)
        for k, v in pairs(t) do
            M[k] = v
        end
    end

    return M
end


vim.api.nvim_command('command! PVStart lua PVServ().start_server()')
vim.api.nvim_command('command! PVStop lua PVServ().stop_server()')
