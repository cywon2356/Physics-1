import tkinter as tk
import math


class ToastSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Toast Sliding Off a Table Simulation (0.75 m vs 3.0 m)")

        # Physical constants
        self.L = 0.15  # Toast length (m)
        self.g = 9.81  # Gravitational acceleration (m/s²)
        self.r_g = math.sqrt(self.L**2 / 12)  # Radius of gyration

        # Table height selection
        self.height_var = tk.DoubleVar(value=0.75)

        # Top control panel
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(fill=tk.X, side=tk.TOP, pady=5)

        tk.Label(
            self.top_frame,
            text="Select Table Height:",
            font=("Arial", 11, "bold")
        ).pack(side=tk.LEFT, padx=10)

        tk.Radiobutton(
            self.top_frame,
            text="Standard Table (0.75 m)",
            variable=self.height_var,
            value=0.75,
            command=self.change_height
        ).pack(side=tk.LEFT, padx=10)

        tk.Radiobutton(
            self.top_frame,
            text="Quadruple-Height Table (3.0 m)",
            variable=self.height_var,
            value=3.0,
            command=self.change_height
        ).pack(side=tk.LEFT, padx=10)

        # Main canvas
        self.canvas_width = 500
        self.canvas_height = 600

        self.canvas = tk.Canvas(
            root,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="white"
        )
        self.canvas.pack()

        # Buttons
        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)

        tk.Button(
            self.btn_frame,
            text="Start",
            command=self.start_sim
        ).pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        tk.Button(
            self.btn_frame,
            text="Reset",
            command=self.reset_sim
        ).pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        self.change_height()

    def change_height(self):
        self.running = False
        self.H = self.height_var.get()

        if self.H == 0.75:
            self.scale = 450 / 0.75
        else:
            self.scale = 450 / 3.0

        self.table_y = 100
        self.table_x = 180

        self.reset_simulation()
        self.draw_scene()

    def reset_simulation(self):
        self.running = False

        self.dt = 0.001
        self.time_elapsed = 0.0

        # Initial conditions
        self.theta = 0.001
        self.r = 0.0001

        self.theta_dot = 0.0
        self.r_dot = 0.01

        self.in_contact = True

        # Free-fall variables
        self.free_fall_x = 0.0
        self.free_fall_y = 0.0

        self.free_fall_vx = 0.0
        self.free_fall_vy = 0.0

    def start_sim(self):
        if not self.running:
            self.running = True
            self.update_physics()

    def reset_sim(self):
        self.running = False
        self.reset_simulation()
        self.draw_scene()

    def update_physics(self):
        if not self.running:
            return

        sub_steps = 15

        for _ in range(sub_steps):

            self.time_elapsed += self.dt

            # Table-contact phase
            if self.in_contact:

                r_ddot = (
                    self.r * self.theta_dot**2
                    + self.g * math.sin(self.theta)
                )

                denominator = self.r**2 + self.r_g**2

                theta_ddot = (
                    self.r *
                    (
                        self.g * math.cos(self.theta)
                        - 2 * self.r_dot * self.theta_dot
                    )
                ) / denominator

                self.r_dot += r_ddot * self.dt
                self.r += self.r_dot * self.dt

                self.theta_dot += theta_ddot * self.dt
                self.theta += self.theta_dot * self.dt

                # Condition for leaving the table edge
                if (
                    self.g * math.cos(self.theta)
                    <=
                    2 * self.r_dot * self.theta_dot
                ):

                    self.in_contact = False

                    self.free_fall_x = (
                        self.r * math.cos(self.theta)
                    )

                    self.free_fall_y = (
                        self.r * math.sin(self.theta)
                    )

                    self.free_fall_vx = (
                        self.r_dot * math.cos(self.theta)
                        -
                        self.r * self.theta_dot * math.sin(self.theta)
                    )

                    self.free_fall_vy = (
                        self.r_dot * math.sin(self.theta)
                        +
                        self.r * self.theta_dot * math.cos(self.theta)
                    )

            # Free-fall phase
            else:

                self.theta += self.theta_dot * self.dt

                self.free_fall_vy += self.g * self.dt

                self.free_fall_x += self.free_fall_vx * self.dt
                self.free_fall_y += self.free_fall_vy * self.dt

        self.draw_scene()

        current_cm_y = (
            self.r * math.sin(self.theta)
            if self.in_contact
            else self.free_fall_y
        )

        if current_cm_y >= self.H:
            self.running = False
            return

        self.root.after(10, self.update_physics)

    def draw_scene(self):

        self.canvas.delete("all")

        # Draw table
        self.canvas.create_rectangle(
            0,
            self.table_y,
            self.table_x,
            self.canvas_height,
            fill="#E6D5AC",
            outline="black"
        )

        self.canvas.create_text(
            self.table_x - 50,
            self.table_y + 25,
            text=f"Table\n({self.H} m)",
            font=("Arial", 12, "bold"),
            justify=tk.CENTER
        )

        # Draw floor
        floor_y = self.table_y + self.H * self.scale

        self.canvas.create_line(
            0,
            floor_y,
            self.canvas_width,
            floor_y,
            width=3
        )

        self.canvas.create_text(
            50,
            floor_y - 15,
            text="Floor",
            font=("Arial", 11, "italic")
        )

        # Center-of-mass coordinates
        if self.in_contact:
            cm_x = (
                self.table_x
                +
                self.r * math.cos(self.theta) * self.scale
            )

            cm_y = (
                self.table_y
                +
                self.r * math.sin(self.theta) * self.scale
            )

        else:

            cm_x = (
                self.table_x
                +
                self.free_fall_x * self.scale
            )

            cm_y = (
                self.table_y
                +
                self.free_fall_y * self.scale
            )

        # Toast geometry
        dx = (
            self.L / 2
            * math.cos(self.theta)
            * self.scale
        )

        dy = (
            self.L / 2
            * math.sin(self.theta)
            * self.scale
        )

        end1_x = cm_x - dx
        end1_y = cm_y - dy

        end2_x = cm_x + dx
        end2_y = cm_y + dy

        nx = -math.sin(self.theta)
        ny = math.cos(self.theta)

        thickness = 5

        # Buttered side (red)
        self.canvas.create_line(
            end1_x + nx * thickness,
            end1_y + ny * thickness,
            end2_x + nx * thickness,
            end2_y + ny * thickness,
            width=4,
            fill="red"
        )

        # Unbuttered side (black)
        self.canvas.create_line(
            end1_x - nx * thickness,
            end1_y - ny * thickness,
            end2_x - nx * thickness,
            end2_y - ny * thickness,
            width=4,
            fill="black"
        )

        # Toast body
        self.canvas.create_line(
            end1_x,
            end1_y,
            end2_x,
            end2_y,
            width=2,
            fill="#D2691E"
        )

        # Center of mass marker
        self.canvas.create_oval(
            cm_x - 3,
            cm_y - 3,
            cm_x + 3,
            cm_y + 3,
            fill="yellow"
        )

        deg = math.degrees(self.theta)

        # Simulation information
        self.canvas.create_text(
            330,
            30,
            text=f"Rotation Angle: {deg:.1f}°",
            anchor="w"
        )

        self.canvas.create_text(
            330,
            55,
            text=f"State: {'On Table' if self.in_contact else 'Free Fall'}",
            anchor="w"
        )

        # Final result
        if not self.running and self.time_elapsed > 0:

            normalized_deg = deg % 360

            if 90 <= normalized_deg < 270:
                result_text = "Result: Toast Lands Butter-Side Down"
                color = "red"
            else:
                result_text = "Result: Toast Lands Butter-Side Up"
                color = "green"

            self.canvas.create_text(
                250,
                520,
                text=result_text,
                fill=color,
                font=("Arial", 14, "bold")
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = ToastSimulation(root)
    root.mainloop()
