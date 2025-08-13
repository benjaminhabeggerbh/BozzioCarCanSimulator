#ifndef COMMON_H
#define COMMON_H

#include <map>
#include <cstdint>

enum button_id_t {
    VW_T5 = 1,
    VW_T6 = 2,
    VW_T61 = 3,
    VW_T7 = 4,
    MB_SPRINTER = 5,
    MB_SPRINTER_2023 = 6,
    JEEP_RENEGADE = 7,
    JEEP_RENEGADE_MHEV = 8,
    MB_VIANO = 9
};

struct ButtonEntry {
    const char* label;
};

using ButtonMap = std::map<button_id_t, ButtonEntry>;

#endif
