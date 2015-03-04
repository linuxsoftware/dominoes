CC=g++
INCLUDE= \
-I .. \
-I /usr/include/glibmm-2.4 \
-I /usr/lib64/glibmm-2.4/include \
-I /usr/include/glib-2.0  \
-I /usr/lib64/glib-2.0/include \
-I /usr/include/gdkmm-2.4 \
-I /usr/lib64/gdkmm-2.4/include \
-I /usr/include/gtkmm-2.4 \
-I /usr/lib64/gtkmm-2.4/include \
-I /usr/include/gtk-2.0 \
-I /usr/lib64/gtk-2.0/include \
-I /usr/include/sigc++-2.0 \
-I /usr/lib64/sigc++-2.0/include \
-I /usr/include/atkmm-1.6 \
-I /usr/include/atk-1.0  \
-I /usr/include/pangomm-1.4 \
-I /usr/lib64/pangomm-1.4/include \
-I /usr/include/giomm-2.4 \
-I /usr/lib64/giomm-2.4/include \
-I /usr/include/pango-1.0 \
-I /usr/include/cairomm-1.0 \
-I /usr/include/cairo \
-I /usr/include/freetype2 \
-I /usr/include/gdk-pixbuf-2.0

CFLAGS=-c -g -Wall $(INCLUDE)
LDFLAGS=-lpangomm-1.4 -latkmm-1.6 -lgdkmm-2.4 -lgtkmm-2.4 \
		-lglibmm-2.4 -lcairomm-1.0 -lsigc-2.0
SRCS= main.cpp playingarea.cpp bone.cpp geometry.cpp
HDRS= playingarea.hpp bone.hpp geometry.hpp

OBJS=$(SRCS:.cpp=.o)
EXE=dominoes

.PHONY: all

all: $(SRCS) $(EXE)
	
$(EXE): $(OBJS) $(HDRS) Makefile
	$(CC) $(LDFLAGS) $(OBJS) -o $@

.cpp.o: $(HDRS)
	$(CC) $(CFLAGS) $< -o $@

.PHONY: clean

clean:
	rm -f *.o $(EXE)
