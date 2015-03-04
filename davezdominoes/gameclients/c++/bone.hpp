#ifndef Bone_hpp__
#define Bone_hpp__

#include <iosfwd>

//TODO #include "../core/bone.hpp"
#include "geometry.hpp"
#include <cairomm/context.h>

namespace Gui 
{
    class PlayingArea;
    class Bone
    {
     public:
        Bone(PlayingArea* area, double x, double y);

        void draw();
        void drawDots(Cairo::RefPtr<Cairo::Context> cr, int numDots);
        void drawDot(Cairo::RefPtr<Cairo::Context> cr, double rx, double ry);
        bool clickedOn(Point here);
        void dragTo(Point dragged);
        bool attachesTo(const Bone& other);
        void reset();

     private:
        PlayingArea * m_area;
        Rect          m_rect;
        double        m_angle;
        Point         m_origPos;
        Point         m_clicked;

 // TODO replace with the real Core Bone
        bool          m_clickedLeft;
     public:
        int           leftDots;
        int           rightDots;
    };

}; // namespace Gui

#endif
