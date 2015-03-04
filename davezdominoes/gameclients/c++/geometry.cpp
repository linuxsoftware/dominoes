
#include "geometry.hpp"

#include <iostream>
#include <math.h>

using namespace std;
using namespace Gui;


Point::Point() : 
    x(0), y(0) 
{
}

Point::Point(double i, double j) : 
    x(i), y(j) 
{
}

bool Point::isOn(const Rect& rect) const
{
    return rect.contains(*this);
}

Rect::Rect() : 
    left(0), top(0), width(0), height(0) 
{
}

Rect::Rect(double l, double t, double w, double h) : 
    left(l), top(t), width(w), height(h) 
{
}

Point Rect::centre() const 
{ 
    return Point(left + width/2, top + height/2); 
}

bool Rect::contains(const Point& point) const
{
    return point.x > left &&
           point.x < left + width &&
           point.y > top &&
           point.y < top + height;
}

bool Rect::intersects(const Rect& other) const
{
    if (top <= other.top && other.top < top + height ||
        other.top <= top && top < other.top + other.height) {
        return left <= other.left && other.left < left + width ||
               other.left <= left && left < other.left + other.width;
    } else {
        return false;
    }
}

Rect Rect::intersection(const Rect& other) const
{
    if (!intersects(other)) {
        return Rect();
    } else {
        double l = max(left, other.left);
        double t = max(top, other.top);
        double w = min(left + width, other.left + other.width) - l;
        double h = min(top + height, other.top + other.height) - t;
        return Rect(l, t, w, h);
    }
}

Rect Rect::unison(const Rect& other) const
{
    double l = min(left, other.left);
    double t = min(top,  other.top);
    double w = max(left + width, other.left + other.width) - l;
    double h = max(top + height, other.top + other.height) - t;
    return Rect(l, t, w, h);
}

void Rect::scale(double factor)
{
    Point c = centre();
    width  *= factor;
    height *= factor;
    left    = c.x - width / 2;
    top     = c.y - height / 2;
}

// returns an angle like atan, but good for the whole circle
double Gui::arctan(double opposite, double adjacent)
{
    double angle;
    if (adjacent == 0.0) {
        if (opposite > 0.0) {
            angle = M_PI_2;
        } else if (opposite == 0.0) {
            angle = 0;
        } else {
            angle = -M_PI_2;
        }
    } else {
        angle = atan(opposite / adjacent);
        if (adjacent < 0.0) {
            angle += M_PI;
        }
    }
    return angle;
}
