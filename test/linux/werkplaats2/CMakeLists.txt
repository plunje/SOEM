
set(SOURCES werkplaats2.c)
add_executable(werkplaats2 ${SOURCES})
target_link_libraries(werkplaats2 soem)
install(TARGETS werkplaats2 DESTINATION bin)
