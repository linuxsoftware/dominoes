#ifndef Geometry_hpp__
#define Geometry_hpp__

#include <iosfwd>

namespace Gui 
{
    class Rect;

    class Point
    {
     public:
        Point();
        Point(double x, double y);
        bool isOn(const Rect& rect) const;

        double x;
        double y;
    };

    class Rect
    {
     public:
        Rect();
        Rect(double left, double top, double width, double height);
        Point centre() const;
        bool contains(const Point& point) const;
        bool intersects(const Rect& other) const;
        Rect intersection(const Rect& other) const;
        Rect unison(const Rect& other) const;
        void scale(double factor);

        double left;
        double top;
        double width;
        double height;
    };

    double arctan(double opposite, double adjacent);

}; // namespace Gui

#endif
