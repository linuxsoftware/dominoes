/* dtrains Copyright (C) 2007 D J Moore
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

#ifndef gtkmm_example_playingarea_h
#define gtkmm_example_playingarea_h

#include <list>
#include <gtkmm/drawingarea.h>
#include "bone.hpp"

namespace Gui
{
    typedef std::list<Bone> Bones;

    class PlayingArea : public Gtk::DrawingArea
    {
     public:
        PlayingArea();
        virtual ~PlayingArea();

     protected:
        //Override default signal handlers
        bool on_expose_event(GdkEventExpose* event);
        bool on_button_press_event(GdkEventButton* event);
        bool on_motion_notify_event(GdkEventMotion*event);
        bool on_button_release_event(GdkEventButton* event);
        void drawBone(int degrees);

     private:
        Bones           m_bones;
        Bones           m_playedBones;
        Bones::iterator m_selectedBone;
    };

}; // namespace Gui

#endif // gtkmm_example_playingarea_h
