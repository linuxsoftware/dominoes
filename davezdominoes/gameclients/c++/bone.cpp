
#include "bone.hpp"
#include "playingarea.hpp"
#include <cairomm/context.h>

#include <iostream>
#include <math.h>

using namespace std;
using namespace Gui;


Bone::Bone(PlayingArea* area, double x, double y) :
    m_area(area),
    m_rect(x - 40, y - 21, 80, 42), 
//    m_rect(x - 30, y - 16, 60, 34), 
    m_angle(0),
    m_origPos(m_rect.centre())
{
    leftDots = 1;
    rightDots = 5;
}

void Bone::draw()
{
    Glib::RefPtr<Gdk::Window> window = m_area->get_window();
    Cairo::RefPtr<Cairo::Context> cr = window->create_cairo_context();
/*
    cr->save();
    cr->set_source_rgb(1, 1, 1);
    cr->paint();
    cr->restore();
    */

    cr->save();
    cr->translate(m_rect.left+m_rect.width/2, m_rect.top+m_rect.height/2);
    cr->rotate(m_angle);

    cr->set_source(Cairo::ImageSurface::create_from_png("marblebg.png"),
//    cr->set_source(Cairo::ImageSurface::create_from_png("shells.png"),
                   -m_rect.width/2, -m_rect.height/2);
    cr->rectangle(-m_rect.width/2, -m_rect.height/2, m_rect.width, m_rect.height);
    cr->fill();

    cr->set_line_cap(Cairo::LINE_CAP_ROUND);
    cr->set_line_join(Cairo::LINE_JOIN_ROUND);
    cr->set_line_width(1);
    cr->set_source_rgb(0.4, 0.4, 0.4);
    cr->rectangle(-m_rect.width/2, -m_rect.height/2, m_rect.width, m_rect.height);
    cr->stroke();

    cr->set_line_cap(Cairo::LINE_CAP_ROUND);
    cr->set_line_width(8);
    cr->translate(-0.25*m_rect.width, 0);
    drawDots(cr, leftDots);
    cr->translate(0.5*m_rect.width, 0);
    drawDots(cr, rightDots);

    cr->restore();
}

void Bone::drawDots(Cairo::RefPtr<Cairo::Context> cr, int numDots)
{
    switch (numDots) {
        case 1:
            cr->set_source_rgb(0.03, 0.52, 0.53);
            drawDot(cr, 0, 0);
            break;
        case 2:
            cr->set_source_rgb(0.13, 0.65, 0.01);
            drawDot(cr, -0.25, -0.5);
            drawDot(cr,  0.25,  0.5);
            break;
        case 3:
            cr->set_source_rgb(1.0, 0.39, 0.43);
            drawDot(cr, -0.25, -0.5);
            drawDot(cr, 0, 0);
            drawDot(cr,  0.25,  0.5);
            break;
        case 4:
            cr->set_source_rgb(0.67, 0.35, 0.24);
            drawDot(cr, -0.25, -0.5);
            drawDot(cr, 0.25, -0.5);
            drawDot(cr, -0.25, 0.5);
            drawDot(cr, 0.25, 0.5);
            break;
        case 5:
            cr->set_source_rgb(0.03, 0.39, 0.75);
            drawDot(cr, -0.25, -0.5);
            drawDot(cr, 0.25, -0.5);
            drawDot(cr, 0, 0);
            drawDot(cr, -0.25, 0.5);
            drawDot(cr, 0.25, 0.5);
            break;
        case 6:
            cr->set_source_rgb(1.0, 0.7, 0.1);
            drawDot(cr, -0.33, -0.5);
            drawDot(cr, 0, -0.5);
            drawDot(cr, 0.33, -0.5);
            drawDot(cr, -0.33, 0.5);
            drawDot(cr, 0, 0.5);
            drawDot(cr, 0.33, 0.5);
            break;
        case 12:
            cr->set_source_rgb(0.8, 0.40, 0.39);
            drawDot(cr, -0.34, -0.55);
            drawDot(cr, -0.116, -0.55);
            drawDot(cr, 0.116, -0.55);
            drawDot(cr, 0.34, -0.55);
            drawDot(cr, -0.34, 0);
            drawDot(cr, -0.116, 0);
            drawDot(cr, 0.116, 0);
            drawDot(cr, 0.34, 0);
            drawDot(cr, -0.34, 0.55);
            drawDot(cr, -0.116, 0.55);
            drawDot(cr, 0.116, 0.55);
            drawDot(cr, 0.34, 0.55);
            break;
    }
}

void Bone::drawDot(Cairo::RefPtr<Cairo::Context> cr, double rx, double ry)
{
    /*
    Glib::RefPtr<Gdk::Window> window = m_area->get_window();
    Cairo::RefPtr<Cairo::Context> cr = window->create_cairo_context();
    */

    cr->move_to(rx*0.5*m_rect.width, ry*0.5*m_rect.height);
    cr->rel_line_to(0.0, 0.0);
    cr->stroke();
}

bool Bone::clickedOn(Point here)
{
    Rect rectLeft(m_rect.left, m_rect.top, m_rect.width/2, m_rect.height);
    Rect rectRight(m_rect.left + rectLeft.width, m_rect.top,  m_rect.width/2, m_rect.height);

    if (rectLeft.contains(here)) {
        m_clicked = rectLeft.centre();
        m_clickedLeft = true;
        return true;

    } else if (rectRight.contains(here)) {
        m_clicked = rectRight.centre();
        m_clickedLeft = false;
        return true;

    } else {
        return false;
    }
}
int toDeg(double a)
{
    return int(a * 180.0 / M_PI);
}
void Bone::dragTo(Point dragged)
{
    Point centre  = m_rect.centre();
    double angle1 = arctan((m_clicked.x - centre.x), (centre.y - m_clicked.y));
    double angle2 = arctan((dragged.x - centre.x),   (centre.y - dragged.y));
//    cout << "angle " << toDeg(m_angle) << " angle1 " << toDeg(angle1) << " angle2 " << toDeg(angle2) << endl;
    m_angle += angle2 - angle1;

    Rect update = m_rect;

    if (m_clickedLeft) {
        m_rect.left = dragged.x + cos(m_angle) * m_rect.width/4 - m_rect.width/2;
        m_rect.top  = dragged.y + sin(m_angle) * m_rect.width/4 - m_rect.height/2;

    } else {
        m_rect.left = dragged.x - cos(-m_angle) * m_rect.width/4 - m_rect.width/2;
        m_rect.top  = dragged.y + sin(-m_angle) * m_rect.width/4 - m_rect.height/2;
    }

    update = update.unison(m_rect);
    update.width  = max(update.width, update.height);
    update.height = max(update.width, update.height);
    update.scale(1.7);

    // force a redraw
    Glib::RefPtr<Gdk::Window> window = m_area->get_window();
    window->invalidate_rect(Gdk::Rectangle((int)update.left, 
                                           (int)update.top, 
                                           (int)update.width, 
                                           (int)update.height), 
                            false);
    m_clicked = dragged;
}

bool Bone::attachesTo(const Bone& other)
{
    // this stuff is hard coded for now :-(
    Point centre  = m_rect.centre();
    Point attachTo;
    double dist = m_rect.width/2 + 5;

    if (m_clickedLeft) {
        attachTo.x = centre.x - cos(m_angle) * dist;
        attachTo.y = centre.y - sin(m_angle) * dist;
        return false;
    } else {
        attachTo.x = centre.x + cos(m_angle) * dist;
        attachTo.y = centre.y + sin(m_angle) * dist;
    }

    Rect rectLeft(other.m_rect.left, other.m_rect.top, 
                  other.m_rect.width/2, other.m_rect.height);
    Rect rectRight(other.m_rect.left + rectLeft.width, other.m_rect.top,  
                   other.m_rect.width/2, other.m_rect.height);
    if (attachTo.isOn(rectRight)) {
        if (other.rightDots != rightDots) {
            return false;
        }
        m_rect.left = other.m_rect.left + m_rect.height/2 -2;
        m_rect.top  = other.m_rect.top + rectRight.height + m_rect.width/4;
        m_angle     = -M_PI_2;

        Glib::RefPtr<Gdk::Window> window = m_area->get_window();
        window->invalidate_rect(Gdk::Rectangle((int)other.m_rect.left -10,
                                               (int)other.m_rect.top-10, 
                                               (int)other.m_rect.width*2 + 20,
                                               (int)other.m_rect.width*2 + 20),
                                false);
        return true;
    }

    return false;
}

void Bone::reset()
{
    Rect update = m_rect;

    m_rect.left = m_origPos.x - m_rect.width/2;
    m_rect.top  = m_origPos.y - m_rect.height/2;
    m_angle = 0;

    // force a redraw
    update.width  = max(update.width, update.height);
    update.height = max(update.width, update.height);
    update.scale(1.8);
    Glib::RefPtr<Gdk::Window> window = m_area->get_window();
    window->invalidate_rect(Gdk::Rectangle((int)update.left, 
                                           (int)update.top, 
                                           (int)update.width, 
                                           (int)update.height), 
                            false);
    update = m_rect;
    update.scale(1.8);
    window->invalidate_rect(Gdk::Rectangle((int)update.left, 
                                           (int)update.top, 
                                           (int)update.width, 
                                           (int)update.height), 
                            false);
}
