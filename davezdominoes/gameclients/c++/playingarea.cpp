/* Copyright (C) 2007 David Moore
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2
 * as published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 */

#include "playingarea.hpp"
#include <cairomm/context.h>

#include <iostream>
using namespace std;
using namespace Gui;

PlayingArea::PlayingArea()
{
    add_events(Gdk::BUTTON_PRESS_MASK | 
               Gdk::POINTER_MOTION_MASK |
               Gdk::POINTER_MOTION_HINT_MASK |
               Gdk::BUTTON_RELEASE_MASK);
    m_selectedBone = m_bones.end();

    m_playedBones.push_back(Bone(this, 400, 350));
    m_playedBones.back().leftDots = 6;
    m_bones.push_back(Bone(this, 200, 650));
    m_bones.back().leftDots = 1;
    m_bones.back().rightDots = 4;
    m_bones.push_back(Bone(this, 300, 650));
    m_bones.back().leftDots = 12;
    m_bones.back().rightDots = 5;
    m_bones.push_back(Bone(this, 400, 650));
    m_bones.back().leftDots = 2;
    m_bones.back().rightDots = 3;
    m_bones.push_back(Bone(this, 500, 650));
    m_bones.back().leftDots = 6;
    m_bones.back().rightDots = 4;
}

PlayingArea::~PlayingArea()
{
}

bool PlayingArea::on_expose_event(GdkEventExpose* event)
{
    // This is where we draw on the window
    Glib::RefPtr<Gdk::Window> window = get_window();
    if (!window) {
        return false;
    }

    for (Bones::iterator i = m_playedBones.begin(); i != m_playedBones.end(); ++i) {
        i->draw();
    }
    for (Bones::iterator i = m_bones.begin(); i != m_bones.end(); ++i) {
        if (i != m_selectedBone) {
            i->draw();
        }
    }
    // always draw the selected bone last, so it is on top
    if (m_selectedBone != m_bones.end()) {
        m_selectedBone->draw();
    }
    return true;
}

bool PlayingArea::on_button_press_event(GdkEventButton* event)
{
    Point here(event->x, event->y);
    for (m_selectedBone = m_bones.begin(); 
         m_selectedBone != m_bones.end(); ++m_selectedBone) {
        if (m_selectedBone->clickedOn(here)) {
            m_selectedBone->dragTo(here);
            break;
        }
    }

    return true;
}

bool PlayingArea::on_motion_notify_event(GdkEventMotion*event)
{
    Point here;
    if (event->is_hint) {
        int xi, yi;
        get_pointer(xi, yi);
        here.x = (double)xi;
        here.y = (double)yi;
    } else {
        here.x = event->x;
        here.y = event->y;
    }

    if (m_selectedBone != m_bones.end()) {
        m_selectedBone->dragTo(here);
        if (m_selectedBone->attachesTo(m_playedBones.back())) {
            m_playedBones.push_back(*m_selectedBone);
            m_bones.erase(m_selectedBone);
            m_selectedBone = m_bones.end();
        }
    }

    return true;
}

bool PlayingArea::on_button_release_event(GdkEventButton* event)
{
    if (m_selectedBone != m_bones.end()) {
        m_selectedBone->reset();
        m_selectedBone = m_bones.end();
    }

    return true;
}

