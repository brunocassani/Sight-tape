#include <iostream>
#include <cmath>
#include <map>
#include <vector>
#include <fstream>


// Define constants
const double g = 9.81;           // Gravitational acceleration. NOTE IT IS LOCALIZED AND PRONE TO ERROR
const double L = 0.6949988;      // Length of arrow (nock throat to tip)
const double W = 0.000575;       // Width of the arrow (diameter)
const double M = 0.0232;         // Mass of the ball (arrow)
const double rho = 1.2;          // Density of air
const double A = L * W;          // Cross-sectional area
const double C = 0.3;            // Drag coefficient
const double v0 = 79.248;        // Initial velocity
const double pi = 3.14159265358979323846; // Pi

double find_x_position(double theta_deg, double dt = 0.005) {
    double theta = theta_deg * pi / 180;  // Launch angle in radians
    double y0 = 0;                        // Initial height

    // Initial position and momentum
    double x = 0;
    double y = y0;
    double vx = v0 * cos(theta);
    double vy = v0 * sin(theta);

    // Time parameters
    double t = 0;

    // Simulation loop
    while (y >= y0) {
        // Update velocity
        double v = sqrt(vx * vx + vy * vy);
        double F_drag = 0.5 * rho * A * C * v * v;
        double ax = -F_drag * (vx / v) / M;
        double ay = -g - F_drag * (vy / v) / M;

        // Update momentum
        vx += ax * dt;
        vy += ay * dt;

        // Update position
        x += vx * dt;
        y += vy * dt;

        // Update time
        t += dt;

        // Check if the ball has returned to the initial y0 height
        if (y <= y0 && t > 0) {
            break;
        }
    }

    // Return the x-position where the y-position is back to y0
    return x;
}

int main() {

    // Initialize a map to store the results
    std::map<int, double> results;

    // Iterate over the target x_distances in increments of 1 yard
    for (int target_distance = 10; target_distance <= 120; target_distance += 1) {
        double theta_low = 0;
        double theta_high = 10;
        double theta_mid;
        double tolerance = 0.4 / 1.09361;
        double x_distance;

        while (theta_high - theta_low > 0.00001) {
            theta_mid = (theta_low + theta_high) / 2;
            x_distance = find_x_position(theta_mid);
            if (fabs(x_distance - target_distance / 1.09361) < tolerance) {
                results[target_distance] = theta_mid;
                break;
            } else if (x_distance < target_distance / 1.09361) {
                theta_low = theta_mid;
            } else {
                theta_high = theta_mid;
            }
        }

        if (theta_high - theta_low <= 0.00001) {
            results[target_distance] = -1;  // If no theta is found for the target distance
        }
    }

    // Write the results to a file
    std::ofstream outfile("angles.txt");
    if (outfile.is_open()) {
        for (const auto& result : results) {
            if (result.second != -1) {
                outfile << "" << result.first << ": " << result.second << "\n";
            }
        }
        outfile.close();
    } else {
        std::cerr << "Unable to open file angles.txt for writing.\n";
    }

    return 0;

}
