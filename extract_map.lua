--
-- !!! NOTE: this script only seems to work AFTER the background map viewer was opened
-- the mgba lua module might not initialize correctly unless parts of the UI are open
--


local WINDOW_MAP_BASE = 0x9800 
local MAP_WIDTH = 32         -- 32 tiles per row in the map
local ENTRY_SIZE = 1         -- 1 byte (8-bit) per Tile ID

function extractTileSequence(startTileX, startTileY, count)
    local offset = (startTileY * MAP_WIDTH + startTileX)
    local start_address = WINDOW_MAP_BASE + offset * ENTRY_SIZE
    
    local tiles = {}
    
    -- Loop to read the requested number of tiles sequentially
    for i = 0, count - 1 do
        local current_address = start_address + i
        local tileID = emu:read8(current_address)
        table.insert(tiles, tileID)
    end
    
    -- Format the output for easy searching
    local hex_sequence = {}
    local decimal_sequence = {}
    for _, id in ipairs(tiles) do
        table.insert(hex_sequence, string.format("%02X", id))
        table.insert(decimal_sequence, tostring(id))
    end

    console:log(string.format("0x%X: %s", start_address, table.concat(hex_sequence, " ")))
    
    return tiles
end

function bg()
    extractTileSequence(1, 12, 18)
    extractTileSequence(1, 13, 18)
    extractTileSequence(1, 14, 18)
    extractTileSequence(1, 15, 18)
    extractTileSequence(1, 16, 18)
end

function all()
    for i = 0,18 do 
        extractTileSequence(0, i, 20)
    end
end